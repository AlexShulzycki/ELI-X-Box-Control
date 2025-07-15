import asyncio

from pipython import GCSDevice

from .StageControl.C884 import C884Interface
from .StageControl.Virtual import VirtualControllerInterface
from .StageControl.DataTypes import StageInfo, ControllerInterface


async def EnumPIUSB():
    """
    Returns a list of connected PI usb devices you can connect to
    :return: ["C-884 SN 425003044", "nuclear-bomb SN 123456"]
    """
    return GCSDevice().EnumerateUSB()


class StageInterface:
    """Interface which moves stages. Does not configure them."""

    def __init__(self, *controller_interfaces: ControllerInterface):
        """Pass in all additional Controller Interfaces in the constructor"""
        self.interfaces: list[ControllerInterface] = list(controller_interfaces)

    async def getAllStages(self) -> list[StageInfo]:
        """
        Gets StageInfo for all configured stages.
        :return:
        """
        res: list[StageInfo] = []
        for interface in self.interfaces:
            connected_stages = interface.stages
            stageinfo = await interface.stageInfo(connected_stages)
            res += stageinfo
        return res

    async def stageInfo(self, identifiers: list[int]) -> list[StageInfo]:
        """
        Gets StageInfo for requested stages.
        :param identifiers: unique identifiers of the requested stages
        :return:
        """
        res = []
        for identifier in identifiers:
            # iterate through interfaces
            for interface in self.interfaces:
                # find the stage by identifier
                if interface.stages.__contains__(identifier):
                    res.append(interface.stageInfo([identifier])[0]) # stageInfo function works with lists
                    break # found it, move on to the next identifier

        return res

    def getRelevantInterface(self, identifier: int) -> ControllerInterface:
        for interface in self.interfaces:
            if interface.stages.__contains__(identifier):
                return interface
        raise Exception("No interface holds the given identifier")


# INIT ALL INTERFACES TOGETHER
C884interface = C884Interface()
Virtualinterface = VirtualControllerInterface()

Stageinterface = StageInterface(C884interface, Virtualinterface)
