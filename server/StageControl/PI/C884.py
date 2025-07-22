import asyncio
from typing import Coroutine, Awaitable, Any

from pipython import GCSDevice
from pydantic import Field, BaseModel

from server.StageControl.DataTypes import StageKind, StageInfo, ControllerInterface, StageStatus
from server.StageControl.PI.DataTypes import PIController, PIControllerStatus, PIConnectionType


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

    @property
    def status(self) -> PIControllerStatus:
        # Update the status with data that doesn't need to be async'd
        self._status.ready = self.ready
        self._status.connected = self.isconnected

        # return the status
        return self._status

    @property
    async def position(self)-> list[float|None]:
        """
        Gets position of stages from controller
        :return:
        """
        self.checkReady("Cannot get position.")
        return self.dict2list(await self.device.qPOS())

    @position.setter
    async def position(self, pos: list[float|None]):
        self.checkReady("Cannot move axes.")

        awaiters = []
        for index, p in enumerate(pos):
            awaiters.append(self.device.MOV(index+1, p))
        await asyncio.gather(*awaiters)

    async def moveChannelTo(self, channel: int, target: float):
        """
        Moves channel(s) to target(s)
        @param channel: Integer of channel to which device(s) is/are connected
        @param target: Float of target position(s)
        """
        self.checkReady("Cannot move axis.")

        await self.device.MOV(channel, target)

    @property
    async def onTarget(self) -> list[bool] | list[None]:
        """
        Returns boolean of whether the axis/axes are on target.
        @return: Boolean or array of booleans of whether the axes are on target.
        """
        self.checkReady()
        return self.dict2list(await self.device.qONT())

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

    @property
    async def range(self) -> list[list[float]]:
        """
        Returns the [min,max] for each channel
        @return: [min,max]
        """
        minrange = self.device.qTMN()
        maxrange = self.device.qTMX()
        minmax: list[list[float]] = []
        for key in self.device.allaxes:
            # If key in one of the range dicts, then put in the actual minmax, otherwise set ranges to [0,0]
            if minrange.keys().__contains__(key):
                minmax.append([minrange[key], maxrange[key]])
            else:
                minmax.append([0,0])

        return minmax

    async def getRange(self):
        """explicitly bypassing the property"""
        return self.range

    async def getSupportedStages(self)-> list[str]:
        if not self.isconnected:
            raise Exception("Not connected!")

        return self.device.qVST()

    def __exit__(self):
        self.closeConnection()

    def __eq__(self, other):
        #  So we can compare controllers to see if they are identical
        return self.__dict__ == other.__dict__



class C884Interface(ControllerInterface):
    """Implementation of ControllerInterface for the C884. Stages are identified by the last number appended to the
    serial number of the controller"""


    def __init__(self):
        super().__init__()
        self.c884: dict[int, C884] = {}
        """Dict of serial number mapped to C884 object"""

    # TODO RESTRUCTURE FOR UPDATED CONTROLLERINTERFACE FORMAT BELOW
    @property
    def stages(self) -> list[int]:
        """Returns unique integer identifiers for each stage"""
        raise NotImplementedError

    def moveTo(self, identifier: int, position: float):
        """Move stage to position"""
        raise NotImplementedError

    @property
    def stageInfo(self) -> dict[int, StageInfo]:
        """Returns StageInfo of connected stages"""
        raise NotImplementedError

    def updateStageInfo(self, identifiers: list[int] = None):
        """Updates StageInfo for the given stages or all if identifier list is empty.
        MUST UPDATE EVENTANNOUNCER"""
        raise NotImplementedError

    @property
    def stageStatus(self) -> dict[int, StageStatus]:
        """Return StageStatus objects for the given stages"""
        raise NotImplementedError

    def updateStageStatus(self, identifiers: list[int] = None):
        """Updates stageStatus for the given stages or all if identifier list is empty.
        MUST UPDATE EVENTANNOUNCER"""
        raise NotImplementedError

    def addStagesByConfigs(self, configs: list[Any]):
        raise NotImplementedError


    @staticmethod
    def deconstruct_Serial_Channel(serial_channel):
        """
        Extracts the channel and serial number from a unique serial-number-channel identifier
        :param serial_channel: serial number with the channel glued to the end
        :return: serial number and channel, separately!
        """
        channel: int = serial_channel % 10  # modulo 10 gives last digit
        sn: int = int((serial_channel - channel) / 10)  # minus channel, divide by 10 to get rid of 0
        return sn, channel


    def addC884(self, config:C884Config):
        if config.serial_number is None:
            raise Exception("No serial number provided")
        self.c884[config.serial_number] = C884(config)

    async def addC884RS232(self, config: C884RS232Config) -> int | Exception:
        """
        Add a C884 connecting via RS232, without knowing the serial number.
        :param config: C884RS232Config, without a serial_number
        :return: the serial number from the connected controller, if successful
        """
        newC884 = C884(config)
        if await newC884.openConnection():
            # we have established a connection, add to dict with serial number
            self.c884[newC884.config.serial_number] = newC884
            # return the serial number
            return newC884.config.serial_number
        else:
            raise Exception(f"Failed to connect to {newC884.config.serial_number}")

    async def onTarget(self, serial_number_channel:list[int]) -> list[bool]:
        """
        On target method with unique serial number identifier
        :param serial_number_channel: serial number of controller, with channel number appended
        :return: if the channel of the given controller is on target
        """
        res: list[bool] = await self.bulkCommand(serial_number_channel, C884.onTarget)
        return res


    async def onTargetController(self, serial_number:int) -> list[bool]|list[None]:
        """
        Ontarget method to get all channels on the controller. NOT IMPLEMENTATION OF ControllerInterface.
        :param serial_number: serial number of controller
        :return: on target status list for each channel. NONE if channel not active/used
        """
        return await self.c884[serial_number].onTarget

    async def moveTo(self, serial_number_channel:int, target: float):
        """
        moveTo implementation of ControllerInterface.
        :param serial_number_channel: serial number of controller, with channel number appended
        :param target: Position to move to, in millimeters
        """
        sn, channel = self.deconstruct_Serial_Channel(serial_number_channel)
        return self.c884[sn].moveChannelTo(channel, target)

    def removeC884(self, serial_number:int):
        self.c884.pop(serial_number).__exit__()

    def getC884(self, serial_number:int):
        return self.c884[serial_number]

    async def updateC884Configs(self, configs: [C884Config]):
        """
        Update the c884s with these configs
        :param configs: array of C884Config objects
        :return:
        """
        awaiters: [Coroutine] = []
        for config in configs:
            # Serial numbers are the keys, we need them!
            if config.serial_number is None:
                raise Exception("No serial number provided")

            # Check if we are dealing with a rs232 connection, and explicitly convert to subclass

            if config.model_dump().keys().__contains__("comport"):
                config = C884RS232Config(**config.model_dump())

            # Otherwise the process is the same as with usb connections
            if self.c884.keys().__contains__(config.serial_number):
                awaiters.append(self.c884[config.serial_number].updateConfig(config))
            else:
                self.c884.update({config.serial_number: C884(config)})
        await asyncio.gather(*awaiters)

    def getC884Configs(self) -> list[C884Config]:
        # Collect configs from each c884
        res: list[C884Config] = []
        for serial_number, c884 in self.c884.items():
            res.append(c884.getConfig())
        return res

    async def getC884Status(self) -> list[C884Status]:
        """
        Gets the status of all the C884 controllers
        :return:
        """
        res: list[Coroutine] = []
        for serial_number, c884 in self.c884.items():
            status = c884.status
            res.append(status)
        return await asyncio.gather(*res)

    async def connect(self, serial_number: int) -> bool:
        """
        Attempt to connect to a C884 on the given com port
        :param serial_number: serial_number to try
        :return:
        """
        return await self.c884[serial_number].openConnection()

    @property
    def stages(self):
        """Returns identifiers of connected stages, in this case the C884 serial no. with the channel stuck the end"""
        res = []
        for cntr in self.c884.values():
            for ch in cntr.connectedChannels:
                res.append(cntr.config.serial_number* 10 + ch) # math is still cheaper than string manipulation
        return res

    async def stageInfo(self, serial_number_channel:list[int]) -> Awaitable[list[StageInfo]]:
        # Avoid making redundant requests, extract as much info as possible
        # Round up the controller serial numbers, create empty dict
        bulkresult = await self.bulkCommand(serial_number_channel, C884.getRange)

        res: list[StageInfo] = []
        for i, result in enumerate(bulkresult):
            # Extract sn and channel from identifier
            sn, channel = self.deconstruct_Serial_Channel(serial_number_channel[i])
            info = StageInfo(
                    # index gymnastics to get the model name from the config
                    model= self.c884.get(sn).config.stages[channel],
                    identifier = serial_number_channel[i],
                    kind=StageKind.linear, # HARDCODED FOR NOW #TODO UN-HARDCODE
                    minimum = result[0], # again, we want the index, not the channel
                    maximum = result[1]
                )
            res.append(info)

        
        res: Awaitable[list[StageInfo]]
        return res

    async def stageStatus(self, serial_number_channel:list[int]) -> Awaitable[list[StageStatus]]:
        awaiters: list[Coroutine] = []
        for identifier in serial_number_channel:
            sn, channel = self.deconstruct_Serial_Channel(identifier)

            connected = self.c884[sn].isconnected
            ready = False
            position = 0.0
            ontarget = False
            if connected:
                ready = self.c884[sn].ready
                position = self.c884[sn].position[channel]
                ontarget = self.c884[sn].onTarget[channel]

            awaiters.append(await StageStatus(
                connected= connected,
                ready= ready,
                position= position,
                ontarget= ontarget
            ))

        return asyncio.gather(awaiters)

    async def bulkCommand(self, serial_number_channel: list[int], command) -> Awaitable[list[Any]]:
        """
        Execute a getter command efficiently across available C884s
        :param serial_number_channel: identifier of the axes we want to work with
        :param command: command we want to issue, from the C884 object
        :return: results in the same order as the axes identifiers were given
        """
        # Avoid making redundant requests, extract as much info as possible
        # Round up the controller serial numbers, create empty dict
        controllers = {}
        for sc in serial_number_channel:
            sn, ch = self.deconstruct_Serial_Channel(sc)
            controllers[sn] = []
        print(controllers)
        # Iterate through each controller serial number in the dict
        for cntr_sn in controllers:
            controllers[cntr_sn]: Awaitable[list[Any]] = command(self.c884[cntr_sn])  # this returns a coroutine!!!

        # Finally, iterate through the request array again and create a parallel response array
        res: list[Any] = []
        for sn_ch in serial_number_channel:
            sn, ch = self.deconstruct_Serial_Channel(sn_ch)

            # await if we have to
            solution = controllers[sn]
            print(type(solution))
            if isinstance(solution, Coroutine):
                controllers[sn] = await solution

            # the relevant dict entry now contains the solution
            res.append((controllers[sn])[ch -1]) # we only want the relevant channel, -1 to get the index.

        res: Awaitable[list[Any]] # make sure to hint that it's an awaitable
        return res

    async def enableCLO(self, serial_number_channel: int):
        sn, ch = self.deconstruct_Serial_Channel(serial_number_channel)
        await self.c884[sn].setServoCLOTrue([ch])