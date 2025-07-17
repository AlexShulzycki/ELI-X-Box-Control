import asyncio
from typing import Awaitable

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
        self.EventAnnouncer: EventAnnouncer = EventAnnouncer(StageInfo, StageStatus)
        self._interfaces: list[ControllerInterface] = []
        for intf in controller_interfaces:
            self.addInterface(intf)

    @property
    def interfaces(self) -> list[ControllerInterface]:
        return self._interfaces

    def addInterface(self, intf: ControllerInterface):
        """
        Adds a ControllerInterface to this interface. Checks if already added, also sets up the
        event announcer.
        :param intf: controller interface to add.
        :return:
        """
        if self.interfaces.__contains__(intf):
            # Already exists here
            return
        # New interface, lets sub to their event announcer and feed it directly into ours
        sub = intf.EventAnnouncer.subscribe(*self.EventAnnouncer.availableDataTypes)
        # We want to listen to stageinfo and stagestatuses
        sub.deliverTo(StageInfo, self.EventAnnouncer.event)
        sub.deliverTo(StageStatus, self.EventAnnouncer.event)

        # All done, finally append to the list
        self._interfaces.append(intf)

    async def updateStageInfo(self, identifiers: list[int] = None):
        """
        Asks relevant controller interface(s) to update their stage info.
        :param identifiers: list of stage identifiers to update stage info for. If none, then all are updated
        """
        awaiters: list[Awaitable] = []
        for cnt in self.interfaces:
            awaiters.append(cnt.updateStageInfo(identifiers))

        await asyncio.gather(*awaiters)


    @property
    def StageInfo(self) -> dict[int, StageInfo]:
        """
        Returns the stage info from each controller.
        :return: dict of identifier -> StageInfo
        """
        res: dict[int, StageInfo] = {}
        for cnt in self.interfaces:
            res.update(cnt.stageInfo)

        return res

    async def updateStageStatus(self, identifiers: list[int] = None):
        """
        Asks relevant controller interface(s) to update their stage status.
        :param identifiers: list of stage identifiers to update stage status for. If none, then all are updated
        """
        awaiters: list[Awaitable] = []
        for cnt in self.interfaces:
            awaiters.append(cnt.updateStageStatus(identifiers))

        await asyncio.gather(*awaiters)

    @property
    def StageStatus(self) -> dict[int, StageStatus]:
        """
        Returns the stage status from each controller.
        :return: dict of identifier -> StageInfo
        """
        res: dict[int, StageStatus] = {}
        for cnt in self.interfaces:
            res.update(cnt.stageStatus)

        return res

    def getRelevantInterface(self, identifier: int) -> ControllerInterface|None:
        """
        Returns relevant controller interface for given identifier.
        :param identifier: identifier to look for
        :return: ControllerInterface, or if the identifier isn't found, None.
        """
        for interface in self.interfaces:
            if interface.stages.__contains__(identifier):
                return interface
        # We haven't found anything, return none.
        return None

    def moveStage(self, identifier: int, position: float) -> bool:
        """
        Move the stage to the given position. Returns True if the stage was moved, raises and
        exception in all other cases.
        :param identifier: identifier of the stage.
        :param position: position to move to
        :return: True, or exception.
        """
        interface = self.getRelevantInterface(identifier)
        if interface is None:
            raise Exception(f"Stage {identifier} doesn't exist")

        interface.moveTo(identifier, position)

        # if we're here, no exception was thrown, so it worked.
        return True




# INIT ALL INTERFACES TOGETHER
C884interface = C884Interface()
Virtualinterface = VirtualControllerInterface()

# TODO Re-Add C884 interface once rewritten
toplevelinterface = MainInterface(Virtualinterface)
