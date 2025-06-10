import asyncio
from collections.abc import Coroutine
from abc import ABC, abstractmethod
from pydantic import BaseModel, Field, field_validator
from enum import Enum

from pipython import GCSDevice

from .StageControl.C884 import C884
from .StageControl.C884 import C884Config, C884RS232Config, C884Status


async def EnumPIUSB():
    """
    Returns a list of connected PI usb devices you can connect to
    :return: ["C-884 SN 425003044", "nuclear-bomb SN 123456"]
    """
    return GCSDevice().EnumerateUSB()

class StageKind(Enum):
    rotational = "rotational"
    linear = "linear"

class StageInfo(BaseModel):
    kind: StageKind = Field(default=False, description="What kind of stage this is")
    minimum: float = Field(default=0, description="Minimum position, in mm.", ge=0)
    maximum: float = Field(description="Maximum position, in mm.", ge=0)

    # Validate that linear stages must have minimums and maximums
    @field_validator("minimum", "maximum")
    def isMinMaxNeeded(cls, v, values):
        if values["kind"] == StageKind.linear and v is None:
            raise ValueError("Linear stage needs minimum and maximum")


class ControllerInterface(ABC):
    """Abstract Base class (ABC) of controller interfaces"""

    @abstractmethod
    @property
    def stages(self) -> [int]:
        """Returns unique integer identifiers for each stage"""
        pass

    @abstractmethod
    def moveTo(self, serial_number:int, position:float):
        """Move stage to position"""
        pass
    @abstractmethod
    def onTarget(self, serial_number:int) -> bool:
        """Check if stage is on target"""
        pass

    @abstractmethod
    def stageInfo(self, serial_number:int) -> StageInfo:
        """Return StageInfo for the given stage"""

class C884Interface(ControllerInterface):
    """Implementation of ControllerInterface for the C884. Stages are identified by the last number appended to the
    serial number of the controller"""

    def __init__(self):
        self.c884: dict[int, C884] = {}
        """Dict of serial number mapped to C884 object"""

    def deconstruct_Serial_Channel(self, serial_channel):
        """
        Extracts the channel and serial number from a unique serial-number-channel identifier
        :param serial_channel: serial number with the channel glued to the end
        :return: serial number and channel, separately!
        """
        channel: int = serial_channel % 10  # modulo 10 gives last digit
        sn: int = int(serial_channel - channel / 10)  # minus channel, divide by 10 to get rid of 0
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

    async def onTarget(self, serial_number_channel:int) -> bool:
        """
        On target method with unique serial number identifier
        :param serial_number_channel: serial number of controller, with channel number appended
        :return: if the channel of the given controller is on target
        """
        sn, channel = self.deconstruct_Serial_Channel(serial_number_channel)
        ontarget = await self.c884[sn].onTarget
        return ontarget[channel -1] # -1 since we want index, so channel 1 is at index 0

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
                res.append(cntr.config.serial_number + 10 + ch) # math is still cheaper than string manipulation

        return res

    async def stageInfo(self, serial_number_channel:int) -> StageInfo:
        serial_number, channel = self.deconstruct_Serial_Channel(serial_number_channel)
        c884 = self.c884[serial_number]
        minmax = await c884.range
        minimum, maximum = minmax[channel-1] # we want the index, since in index world 1 actually equals 0

        # Construct the StageInfo object
        res = StageInfo(
            kind=StageKind.linear, # HARDCODED FOR NOW #TODO UN-HARDCODE
            minimum = minimum,
            maximum = maximum
        )
        return res


class StageInterface:
    """Interface which moves stages. Does not configure them."""

    def __init__(self, *args: [ControllerInterface]):
        """Pass in all additional Controller Interfaces in the constructor"""


# INIT ALL INTERFACES TOGETHER
C884interface = C884Interface()



# standa interface etc etc