import asyncio
from typing import Coroutine, Awaitable, Any

from pipython import GCSDevice

from server.StageControl.DataTypes import StageKind, StageInfo, ControllerInterface, StageStatus
from server.StageControl.PI.DataTypes import PIController, PIControllerStatus, PIConnectionType, PIStageInfo


class ControllerNotReadyException(Exception):
    def __init__(self, message = ""):
        self.message = f"Controller not ready! {message}"
        super().__init__(self.message)

def sn_in_device_list(SN: int, enumerate_usb: [str]):
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

    # TODO RECOGNIZE HOW MANY CHANNELS A CONTROLLER HAS AND THUS MITIGATE USER IDIOCY

    AXIS SETUP PROCESS:
    1 Connect the controller, run openConnection(), make sure its plugged in and you have the right com port etc etc
    2 Tell the controller what stages are connected with CST
    2 Check if the axes are turned on with qSVO, otherwise turn on with SVO
    3 Check if axes are referenced with qFRF()
    4 Reference axis with FRF(), this thing will move so be careful
    5 Set soft limits??? working on that. You an also check if the type of axis has to be FRF'd by asking qRON()
    """

    def __init__(self, status: PIControllerStatus):
        """
        Initialize the controller and update/reference what's requested in the config. Throws an exception if it fails.

        A device which is not powered or improperly connected will raise an error!
        """

        # Start up GCS device
        self.device: GCSDevice.gcsdevice = GCSDevice("C-884").gcsdevice
        """GCSDevice instance, DO NOT ACESS/MODIFY OUTSIDE OF THE C884 CLASS"""

        super().__init__(status)

    async def updateFromStatus(self, status: PIControllerStatus):
        """
        Compares given status with current status of controller, and changes settings if necessary.
        :param status: Status object with the controller state that we want.
        :return:
        """

        if not self.status.connected and status.connected:
            # open connection handles channel_amount as well
            await self.openConnection(status)

        if status.stages != self.status.stages:
            await self.loadStagesToC884(status.stages)

        if status.clo != self.status.clo:
            await self.setServoCLO(status.clo)

        if status.referenced != self.status.referenced:
            await self.reference(status.referenced)


    @staticmethod
    def list2dict(fromList: list[Any]) -> dict[int, Any]:
        """
        Helper function that converts an array where each entry is one axis, i.e [True, None, 1.4] to a dictionary.
        :param fromList: list to convert to dict
        :return: dict in the correct format
        """
        request_dict = {}

        for i, value in enumerate(fromList):
            # Ignore none values
            if value is None:
                continue
            else:
                request_dict[i + 1] = value

        return request_dict



    def dict2list(self, fromController: dict) -> list[Any|None]:
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

        res =  self.device.qCST()

        return self.dict2list(res)

    async def loadStagesToC884(self, stages: list[str]):
        """
        Loads stages per axis onto the controller, from self.stages
        :return:
        """
        self.checkReady()

        try:
            self.device.CST(self.list2dict(stages))
        except Exception as e:
            print(e)
            raise e

    @property
    async def error(self)-> str | None:
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
        return self.isavailable # for now just isavailables

    def checkReady(self, message: str = ""):
        """ Raises ControllerNotReady exception if controller is not ready"""
        if not self.ready:
            raise ControllerNotReadyException(message)

    @property
    async def mustBeReferencedFirst(self) -> list[bool| None]:
        """
        Returns true for axes which need to be referenced
        :return:
        """
        self.checkReady()
        return self.dict2list(self.device.qRON(self.device.axes))

    @property
    async def isReferenced(self) -> list[bool| None]:
        """
        Returns true for axes already referenced
        :return:
        """
        self.checkReady()
        return self.dict2list(self.device.qFRF(self.device.axes))

    @property
    async def servoCLO(self)-> list[bool| None]:
        """
        Checks if servo is in closed loop operation, i.e. turned on
        :return:
        """
        self.checkReady()
        return self.dict2list(self.device.qSVO(self.device.axes))


    async def setServoCLO(self, axes: list[bool] = None):
        """
        Try to set all axes to closed loop operation, i.e. enabling them. if no list is given, all configured axes will
        have their CLO set to true
        :param axes:
        :return:
        """
        if axes is None:
            axes = self.device.axes
            self.device.SVO(axes, [True] * len(axes))
        else:
            self.device.SVO(axes)

    async def reference(self, axes: list[bool] = None):
        """
        Reference the given axes. If none, reference all axes.
        :param axes: for example [1, 2, 4] for servos on channel 1, 2, and 4
        :return:
        """
        self.checkReady()
        if axes is None:
            axes = self.device.axes
            self.device.FRF(axes) #, [True] * len(axes))
        else:
            self.device.FRF(axes)


    async def refreshFullStatus(self):
        status = PIControllerStatus(
            SN=self.status.SN,
            model = self.status.model,
            connection_type = self.status.connection_type,
            connected = self.isconnected,
            ready = self.ready,
            # For now, we assume the stage is not ready, so everything else is in their defaults
        )
        # if we are doing rs232, check the additional fields
        if status.connection_type is PIConnectionType.rs232:
            status.baud_rate = self.status.baud_rate
            status.comport = self.status.comport

        # If the controller is ready, then we query for the rest of the status information
        if status.ready:
            status.referenced = await self.isReferenced,
            status.clo = await self.servoCLO,
            status.error = await self.error,
            status.stages = await self.loadStagesFromC884()

        self._status = status

        # update other bits and bobs
        await self.update_range()
        await self.update_position()
        await self.update_onTarget()
        await self.update_range()

    @property
    def status(self) -> PIControllerStatus:
        # Update the status with data that doesn't need to be async'd
        self._status.ready = self.ready
        self._status.connected = self.isconnected

        # return the status
        return self._status

    async def refreshPosOnTarget(self):
        await self.update_onTarget()
        await self.update_position()

    async def update_position(self):
        """
        Gets position of stages from controller
        :return:
        """
        self.checkReady("Cannot get position.")
        self._status.position = self.dict2list(await self.device.qPOS())

    async def moveChannelTo(self, channel: int, target: float):
        """
        Moves channel(s) to target(s)
        @param channel: Integer of channel to which device(s) is/are connected
        @param target: Float of target position(s)
        """
        self.checkReady("Cannot move axis.")

        await self.device.MOV(channel, target)

    async def update_onTarget(self):
        """
        Returns boolean of whether the axis/axes are on target.
        @return: Boolean or array of booleans of whether the axes are on target.
        """
        self.checkReady()
        self._status.on_target = self.dict2list(await self.device.qONT())

    async def openConnection(self, config: PIControllerStatus) -> bool:
        """
        Opens connection to controller device if not already connected
        :return: true if successful or already connected, false otherwise
        """
        if self.device.connected:
            return True
        else:
            # try to connect
            try:
                if config.connection_type is PIConnectionType.rs232:
                    print("Connecting with rs232")
                    # connect with rs232
                    self.device.ConnectRS232(config.comport, config.baudrate)

                    # Grab serial number
                    SN = int(self.device.qIDN().split(", ")[-2])

                    # Check if serial number matches config status
                    if config.SN != SN:
                        raise Exception(f"Serial number of RS232 controller does not match configuration: {SN}")

                else:
                    # connect with usb
                    # Check if we have this serial number connected via usb
                    exists = sn_in_device_list(config.serial_number, self.device.EnumerateUSB())

                    if exists:
                        self.device.ConnectUSB(config.serial_number)
                    else:
                        raise Exception(f"USB Controller with given serial number not connected: {config.SN}")

                # set the channel amount
                self._status.channel_amount = len(self.device.allaxes)
                return self.device.connected

            except Exception as e:
                # close the connection explicitly just to be sure
                self.closeConnection()
                raise e

    def closeConnection(self):
        """
        Closes connection to the controller device
        """
        self.device.CloseConnection()

    async def update_range(self):
        """
        Returns the [min,max] for each channel
        @return: [min,max]
        """
        minrange = self.device.qTMN()
        maxrange = self.device.qTMX()

        for i in range(self.status.channel_amount):
            if self.status.stages[i] is "NOSTAGE":
                self._status.min_max[i] = None
            else:
                self._status.min_max[i] = [minrange[i+1], maxrange[i+1]]


    async def getSupportedStages(self)-> list[str]:
        if not self.isconnected:
            raise Exception("Not connected!")

        return self.device.qVST()

    def shutdown_and_cleanup(self):
        self.__exit__()

    def __exit__(self):
        self.closeConnection()

    def __eq__(self, other):
        #  So we can compare controllers to see if they are identical
        return self.__dict__ == other.__dict__