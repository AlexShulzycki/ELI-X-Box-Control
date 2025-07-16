import asyncio

from pipython import GCSDevice
from pydantic import BaseModel

from .StageControl.C884 import C884Interface
from .StageControl.Virtual import VirtualControllerInterface
from .StageControl.DataTypes import StageInfo, ControllerInterface, EventAnnouncer, StageStatus


async def EnumPIUSB():
    """
    Returns a list of connected PI usb devices you can connect to
    :return: ["C-884 SN 425003044", "nuclear-bomb SN 123456"]
    """
    return GCSDevice().EnumerateUSB()


class MainInterface:
    """Interface that takes in identifier then communicates with relevant controller interface.
    Does not configure them. Also provides an EventAnnouncer for StageInfo and StageStatus"""

    #TODO Finish up the controller interfaces, reformat this into a way that receives events and interfaces
    # with controller interface functions.

    def __init__(self, *controller_interfaces: ControllerInterface):
        """Pass in all additional Controller Interfaces in the constructor"""
        self._interfaces: list[ControllerInterface] = []
        for intf in controller_interfaces:
            self.addInterface(intf)
        self.EventAnnouncer: EventAnnouncer = EventAnnouncer(StageInfo, StageStatus)

    @property
    def interfaces(self) -> list[ControllerInterface]:
        return self._interfaces

    def addInterface(self, intf: ControllerInterface):
        if self.interfaces.__contains__(intf):
            # Already exists here
            return
        # New interface, lets sub to their event announcer and feed it directly into ours
        sub = intf.EventAnnouncer.subscribe(self.EventAnnouncer.availableDataTypes)
        sub.deliverTo(StageInfo, self.EventAnnouncer.event)
        sub.deliverTo(StageStatus, self.EventAnnouncer.event)

        # All done, finally append to the list
        self._interfaces.append(intf)

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

toplevelinterface = MainInterface(C884interface, Virtualinterface)
