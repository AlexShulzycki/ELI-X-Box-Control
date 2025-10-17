import asyncio
from typing import Coroutine, Awaitable, Any

from pipython import GCSDevice

from server.Settings import SettingsVault
from server.StageControl.DataTypes import Notice, StageKind, ConfigurationUpdate
from server.StageControl.PI.DataTypes import PIController, PIConfiguration, PIConnectionType, PIStageInfo, PIStage


class ControllerNotReadyException(Exception):
    def __init__(self, message=""):
        self.message = f"Controller not ready! {message}"
        super().__init__(self.message)


def sn_in_device_list(SN: int, enumerate_usb: list[str]):
    """
    Checks if serial number is in a list of enumerated USB devices
    :param SN: serial number to check
    :param enumerate_usb: enumerated usb devices from gcsdevice.EnumerateUSB()
    :return: if it is in the enumeration list
    """
    exists = False
    for entry in enumerate_usb:
        if int(entry.split(" ")[-1]) == SN:
            exists = True
    return exists


class C884(PIController):
    """
    Class used to interact with a single PI C-884 controller.
    Remember to close the connection once you are done with the controller to avoid blocking the com port - especially
    during setup.

    AXIS SETUP PROCESS:
    1 Connect the controller, run openConnection(), make sure its plugged in and you have the right com port etc etc
    2 Tell the controller what stages are connected with CST
    2 Check if the axes are turned on with qSVO, otherwise turn on with SVO
    3 Check if axes are referenced with qFRF()
    4 Reference axis with FRF(), this thing will move so be careful
    5 Set soft limits??? working on that. You an also check if the type of axis has to be FRF'd by asking qRON()
    """
    # TODO Set a timeout for referencing, or be able to detect some kind of errors when referencing

    def __init__(self):
        """
        Initialize the controller and update/reference what's requested in the config. Throws an exception if it fails.

        A device which is not powered or improperly connected will raise an error!
        """

        # Start up GCS device
        self.device: GCSDevice.gcsdevice = GCSDevice("C-884").gcsdevice
        """GCSDevice instance, DO NOT ACESS/MODIFY OUTSIDE OF THE C884 CLASS"""
        self.being_referenced = []
        """List of axes we are currently referencing, because PI doesn't know :)"""
        super().__init__()

    async def updateFromConfig(self, config: PIConfiguration):
        """
        Compares given status with current status of controller, and changes settings if necessary. If a new valid stage
        appears, send an event.
        :param config: Status object with the controller state that we want.
        :return:
        """

        # if we are a fresh object without a config, lets make one
        if self.config is None:
            self._config = PIConfiguration(
                SN=config.SN,
                model=config.model,
                connection_type=config.connection_type,
                comport=config.comport,
                channel_amount=config.channel_amount
                # else we get a validation error, we are not actually bypassing anything here because this is
                # explicitly checked with the user input and further down in the connection function.
            )

        if not (self.config.connected and config.connected):
            # open connection handles channel_amount as well
            print("opening connection")
            self.EA.event(ConfigurationUpdate(SN=config.SN, message="Connecting"))
            await self.openConnection(config)

        # send an update for the user
        update = ConfigurationUpdate(SN=config.SN, message="New configuration received")
        self.EA.event(update)

        # if no stages are given, we read the stages from the controller and not overwrite anything
        if len(config.stages) == 0:
            # Do a full status refresh and return
            await self.refreshFullStatus()
            return

        # Otherwise, we now need to update the stages
        print("loading new stages")
        await self.loadStagesToC884(config.stages)


        print("setting CLO")
        await self.setServoCLO(config.stages)


        print("Referencing")
        await self.reference(config.stages)

        # Do a full status refresh
        await self.refreshFullStatus()


    def dict2list(self, fromController: dict) -> list[Any | None]:
        """
        Helper function.
        Converts dict received from the controller into a list, putting a None where no stage is connected
        """
        res = [None] * len(self.device.allaxes)
        # The returned dict will not contain keys of stages which are not connected
        for i in self.device.axes:
            res[int(i) - 1] = fromController[f"{i}"]

        return res

    async def loadStagesFromC884(self):
        """
        Queries and returns stages configured per axis from controller.
        :return: The stages configured on the controller.
        """
        self.checkReady()

        cst = self.device.qCST()
        return cst

    async def loadStagesToC884(self, stages: dict[str, PIStage]):
        """
        Loads stages per axis onto the controller, from self.stages
        :return:
        """
        self.checkReady()

        req = {}
        # Prepopulate with NOSTAGE
        for i in range(self.config.channel_amount):
            req[i + 1] = "NOSTAGE"
        # Replace NOSTAGE with stage name
        for stage in stages.values():
            req[stage.channel] = stage.device
        try:
            self.device.CST(req)
            # Save to non-volatile memory so we have it again on next startup
            self.device.WPA()
            # if we're here then we successfully updated stages
            self._config.stages = stages
        except Exception as e:
            print(e)
            raise e

    @property
    async def error(self) -> str | None:
        """
        Gets the error from controller
        :return: the error read from the controller
        """
        if self.ready:
            return str(self.device.GetError())
        else:
            return "Controller not ready."

    @property
    def isavailable(self) -> bool:
        return self.device.isavailable

    @property
    def isconnected(self) -> bool:
        return self.device.IsConnected()

    @property
    def ready(self) -> bool:
        return self.isavailable  # for now just isavailable

    def checkReady(self, message: str = ""):
        """ Raises ControllerNotReady exception if controller is not ready"""
        if not self.ready:
            raise ControllerNotReadyException(message)

    @property
    async def mustBeReferencedFirst(self) -> list[bool | None]:
        """
        Returns true for axes which need to be referenced
        :return:
        """
        self.checkReady()
        return self.dict2list(self.device.qRON(self.device.axes))

    @property
    async def isReferenced(self) -> dict[str, bool]:
        """
        Returns true for axes already referenced
        :return:
        """
        self.checkReady()
        return self.device.qFRF(self.device.axes)

    @property
    async def servoCLO(self) -> list[bool | None]:
        """
        Checks if servo is in closed loop operation, i.e. turned on
        :return:
        """
        self.checkReady()
        return self.device.qSVO(self.device.axes)

    async def setServoCLO(self, stages: dict[str, PIStage] = None):
        """
        Try to set all axes to closed loop operation, i.e. enabling them. if no list is given, all configured axes will
        have their CLO set to true
        :return:
        """
        if stages is None:
            self.device.SVO(self.device.axes, [True] * len(self.device.axes))
        else:
            # if there are non-None values for a stage which is a NOSTAGE, set it to none,
            # or else GCS will throw an error

            req = {}
            for stage in stages.values():
                req[stage.channel] = stage.clo

            # Only do a request if our request is not empty, else an exception will be thrown
            if len(req.values()) != 0:
                self.device.SVO(req)

    async def reference(self, stages: dict[str, PIStage]):
        """
        Reference the given axes. If none, reference all axes. We cannot "dereference" axes,
        so no worries about accidentally doing that.
        :param stages: PIStage objects we pull data from.
        :return:
        """
        # clear the list of stages we are currently referencing
        self.being_referenced = []

        # check if we are ready, if we are requesting anything to be referenced in the first place
        self.checkReady()
        if stages is None:
            return

        else:
            req = []
            # Check against the current referenced axes, we do not want to reference already references stages.
            refd = await self.isReferenced
            # Go through each stage configuration.
            for stage in stages.values():
                if stage.referenced and refd.__contains__(str(stage.channel)) and refd[str(stage.channel)]:
                    # Already referenced, no need to re-reference
                    continue
                elif stage.referenced:
                    # We would like to request this stage to be referenced
                    req.append(stage.channel)
                    # add to the list of stages we are referencing
                    self.being_referenced.append(stage.channel)

            if len(req) != 0:
                # Ask the controller to reference. Make sure the request is not empty.
                self.device.FRF(req)
                await self.refreshFullStatus()  # do this because sometimes it shows as not ref'd.

    async def refreshFullStatus(self):
        print("refresh full status")

        status = PIConfiguration(
            SN=self.config.SN,
            model=self.config.model,
            connection_type=self.config.connection_type,
            connected=self.isconnected,
            channel_amount=self.config.channel_amount,
            ready=self.ready,
            comport=0,  # for validation
            # For now, we assume the stage is not ready, so everything else is in their defaults
        )
        # if we are doing rs232, check the additional fields
        if status.connection_type is PIConnectionType.rs232:
            status.baud_rate = self.config.baud_rate
            status.comport = self.config.comport


        # If the controller is ready, then we query for the rest of the status information
        if status.ready:

            # We now try to read information to disk, namely whether
            # the stage is linear or rotational
            SV = SettingsVault()
            await SV.load_all()

            # Check if ref'd, clo'd and the device name
            refd, clod, dev = await asyncio.gather(self.isReferenced, self.servoCLO, self.loadStagesFromC884())
            for ax in self.device.axes:

                # get device data saved on disk
                fetched = self.fetchPIStageData(dev[ax], SV.readonly["PIStages"])

                # Generate the PIStage object from what we learned
                try:
                    status.stages[ax] = PIStage(
                        channel=ax,
                        referenced=refd[ax],
                        clo=clod[ax],
                        device=dev[ax],
                        kind=StageKind(fetched["type"])
                    )
                except Exception as e:
                    raise Exception(f"Error reading stages from settings/readonly/PIStages.json: {e}")


        self._config = status

        # update parameters which directly save to the self.config
        await asyncio.gather(self.refreshPosOnTarget(), self.update_ranges())

        # Send an info update, status is handled in pos on target
        for info in self.stageInfos.values():
            self.EA.event(info)

    @property
    def config(self) -> PIConfiguration:

        # if we are none, return none
        if self._config is None:
            return None

        # Update the status with data that doesn't need to be async'd
        self._config.ready = self.ready
        self._config.connected = self.isconnected

        # return the status, but as a copy, we don't want anyone to access this.
        return self._config.__copy__()

    async def refreshPosOnTarget(self):
        await asyncio.gather(self.update_onTarget(), self.update_position())

        # Send a status update
        for status in self.stageStatuses.values():
            self.EA.event(status)

    async def update_position(self):
        """
        Gets position of stages from controller
        :return:
        """
        self.checkReady("Cannot get position.")
        # ensure float type
        for channel, pos in self.device.qPOS().items():
            if self.config.stages.__contains__(channel):
                self._config.stages[channel].position = float(pos)

    async def moveTo(self, channel: str, target: float):
        """
        Moves channel(s) to target(s)
        @param channel: Integer of channel to which device(s) is/are connected
        @param target: Float of target position(s)
        """
        self.checkReady("Cannot move axis.")

        self.device.MOV(channel, target)

    async def moveBy(self, channel, step):
        self.checkReady("Cannot move axis.")

        # MVR is for relative, but it is relative to the last commanded
        # target position, not current position.
        position = self.dict2list(self.device.qPOS())
        self.device.MOV(channel, position[channel - 1] + step)

    async def update_onTarget(self):
        """
        Returns boolean of whether the axis/axes are on target.
        @return: Boolean or array of booleans of whether the axes are on target.
        """
        self.checkReady()
        for key, ont in self.device.qONT().items():
            if self.config.stages.__contains__(key):
                self._config.stages[key].on_target = ont

    async def openConnection(self, config: PIConfiguration) -> bool:
        """
        Opens connection to controller device if not already connected
        :return: true if successful or already connected, false otherwise
        """
        if not self.device.connected:
            # try to connect
            try:
                if config.connection_type is PIConnectionType.rs232:
                    print("Connecting with rs232")
                    # connect with rs232
                    self.device.ConnectRS232(config.comport, config.baud_rate)

                    # Grab serial number
                    SN = int(self.device.qIDN().split(", ")[-2])
                    # update comport
                    self._config.comport = config.comport
                    # Check if serial number matches config status
                    if config.SN != SN:
                        self.device.close()
                        raise Exception(f"Serial number of RS232 controller does not match configuration: {SN}")

                else:
                    # connect with usb
                    # Check if we have this serial number connected via usb
                    exists = sn_in_device_list(config.SN, self.device.EnumerateUSB())

                    if exists:
                        self.device.ConnectUSB(config.SN)
                    else:
                        self.device.close()
                        raise Exception(f"USB Controller with given serial number not connected: {config.SN}")


            except Exception as e:
                # close the connection explicitly just to be sure
                self.closeConnection()
                raise e

        # check the channel amount. Automatically sets itself.
        ch_amount = len(self.device.allaxes)
        self._config.channel_amount = ch_amount
        return self.device.connected

    def closeConnection(self):
        """
        Closes connection to the controller device
        """
        self.device.CloseConnection()

    async def update_ranges(self):
        """
        Updates the [min,max] for each channel
        """
        self.checkReady()
        minrange = self.device.qTMN()
        maxrange = self.device.qTMX()

        # Go through each stage in the config and update the minmax
        for stage in self._config.stages.values():
                stage.min_max = ([minrange[str(stage.channel)], maxrange[str(stage.channel)]])

    async def getSupportedStages(self) -> list[str]:
        if not self.isconnected:
            raise Exception("Not connected!")

        return self.device.qVST()

    async def is_configuration_configured(self):

        # The only PI configuration we need to query periodically for is if everything is referenced
        refstate = self.device.qFRF()
        print("refstate, being_referenced", refstate, self.being_referenced)
        message = "Referencing"

        for reffing in self.being_referenced:
            if refstate.__contains__(str(reffing)):
                # we have it (we should!)
                if refstate.get(str(reffing)):
                    # add to the message and remove from list of axes being referenced
                    message += f", Channel {reffing} referenced "
                    self.being_referenced.remove(reffing)
            else:
                # something has gone wrong! tell the user and remove from list
                self.EA.event(ConfigurationUpdate(SN=self.config.SN,message=f"could not find channel {reffing}", error=True))
                self.being_referenced.remove(reffing)


        # Construct the configuration update
        if len(self.being_referenced)==0:
            message = "Ready"

        await self.refreshFullStatus()

        update = ConfigurationUpdate(
            SN=self.config.SN,
            message = message,
            configuration = self.config.toPIAPI(),
            finished = len(self.being_referenced)==0,
        )
        self.EA.event(update)


        # Check if controller is ready, if True we don't need to run this function again
        return self.config.SN, len(self.being_referenced)==0

    def shutdown_and_cleanup(self):
        self.__exit__()

    # adding a bunch of exit handlers to triple make sure it disconnects gracefully
    # and doesn't keep hogging the com port (for rs232 mainly, and no i'm not gonna
    # check which connection type is being used to save 1 * 10^-100 seconds).

    def __exit__(self):
        self.closeConnection()

    def __eq__(self, other):
        #  So we can compare controllers to see if they are identical
        return self.__dict__ == other.__dict__
