import asyncio
from collections.abc import Coroutine

from pipython import GCSDevice

from .StageControl.C884 import C884
from .StageControl.C884 import C884Config, C884RS232Config, C884Status


async def EnumPIUSB():
    """
    Returns a list of connected PI usb devices you can connect to
    :return: ["C-884 SN 425003044", "nuclear-bomb SN 123456"]
    """
    return GCSDevice().EnumerateUSB()

class C884Interface:

    def __init__(self):
        self.c884: dict[int, C884] = {}
        """Dict of serial number mapped to C884 object"""

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

    async def onTarget(self, serial_number) -> list[bool]|list[None]:
        return await self.c884[serial_number].onTarget

    async def moveTo(self, serial_number:int, axis: int, target: float):
        return self.c884[serial_number].moveChannelTo(axis, target)

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


C884interface = C884Interface()