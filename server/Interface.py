from pipython import GCSDevice

from .StageControl.C884 import C884Interface
from .StageControl.DataTypes import StageInfo, ControllerInterface


async def EnumPIUSB():
    """
    Returns a list of connected PI usb devices you can connect to
    :return: ["C-884 SN 425003044", "nuclear-bomb SN 123456"]
    """
    return GCSDevice().EnumerateUSB()


class StageInterface:
    """Interface which moves stages. Does not configure them."""

    def __init__(self, *controller_interfaces: [ControllerInterface]):
        """Pass in all additional Controller Interfaces in the constructor"""
        self.interfaces: list[ControllerInterface] = list(controller_interfaces)

    def getAllStages(self) -> list[StageInfo]:
        """
        Gets StageInfo for all configured stages.
        :return:
        """
        res: [StageInfo] = []
        for interface in self.interfaces:
            res.append(interface.stageInfo(interface.stages))
        return res

    def stageInfo(self, identifiers: [int]) -> list[StageInfo]:
        """
        Gets StageInfo for requested stages.
        :param identifiers: unique identifiers of the requested stages
        :return:
        """
        res = []
        for identifier in identifiers:
            for interface in self.interfaces:
                if interface.stages.__contains__(identifier):
                    res.append(interface.stageInfo([identifier])[0]) # since this returns a list
                    break # found it, move on to the next identifier

        return res


# INIT ALL INTERFACES TOGETHER
C884interface = C884Interface()

Stageinterface = StageInterface(C884interface)
