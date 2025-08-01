from typing import Any

from pydantic import Field, BaseModel

from .DataTypes import StageKind, StageInfo, StageStatus, ControllerInterface, ControllerSettings, updateResponse, \
    StageRemoved


class VirtualSettings(ControllerSettings):

    def __init__(self):
        super().__init__()
        self.virtualstages: dict[int, VirtualStage] = {}

    @property
    def currentConfiguration(self) -> list[Any]:
        res = []
        for v in self.virtualstages.values():
            res.append(v.stageInfo)
        return res

    async def configurationChangeRequest(self, requests: list[StageInfo]) -> list[updateResponse]:
        res = []
        for request in requests:
            try:
                    self.virtualstages[request.identifier] = VirtualStage(request)
                    res.append(updateResponse(
                        identifier=request.identifier,
                        success=True,
                    ))
                    # success, send an event update
                    self.EventAnnouncer.event(self.virtualstages[request.identifier].stageInfo)
            except Exception as e:
                res.append(updateResponse(
                    identifier = request.identifier,
                    success = False,
                    error = str(e),
                ))
        return res

    async def removeConfiguration(self, identifier: int):
        if identifier in self.virtualstages.keys():
            self.virtualstages.pop(identifier)
            self.EventAnnouncer.event(StageRemoved(identifier = identifier))
            return True
        else:
            return False

    @property
    def configurationFormat(self):
        return StageInfo

    def getDataTypes(self):
        return [StageInfo, StageStatus]


class VirtualStage:
    def __init__(self, config: StageInfo):
        self.stageInfo = config
        self.stageStatus = StageStatus(identifier= config.identifier, connected=True, ready=True, position=config.minimum, ontarget=True)


class VirtualControllerInterface(ControllerInterface):

    def __init__(self):
        super().__init__()
        self.settings:VirtualSettings = VirtualSettings()
        # forward events
        sub = self.settings.EventAnnouncer.subscribe(StageInfo, StageRemoved)
        sub.deliverTo(StageInfo, self.EventAnnouncer.event)
        sub.deliverTo(StageRemoved, self.EventAnnouncer.event)

    @property
    def name(self) -> str:
        return "Virtual"

    @property
    def stages(self) -> list[int]:
        """Returns unique integer identifiers for each stage"""
        return list(self.settings.virtualstages.keys())

    def moveTo(self, serial_number: int, position: float):
        """Move stage to position"""
        self.settings.virtualstages[serial_number].stageStatus.position = position
        self.settings.virtualstages[serial_number].stageStatus.ontarget = True
        self.EventAnnouncer.event(self.stageStatus)

    async def updateStageInfo(self, identifiers: list[int] = None):
        """Update stage info objects"""
        # loop through I cant be bothered
        for v in self.settings.virtualstages.values():
            print("updatestageinfo sending rn")
            self.EventAnnouncer.event(v.stageInfo)
        return

    @property
    def stageInfo(self) -> dict[int, StageInfo]:
        e = {} # dunno why I called it e
        for v in self.settings.virtualstages.values():
            e[v.stageInfo.identifier] = v.stageInfo
        return e

    async def updateStageStatus(self, identifiers: list[int] = None):
        # loop through I cant be bothered
        for v in self.settings.virtualstages.values():
            self.EventAnnouncer.event(v.stageStatus)
        return

    @property
    def stageStatus(self) -> dict[int, StageStatus]:
        """Return StageStatus objects for the given stages"""
        e = {}  # dunno why I called it e
        for v in self.settings.virtualstages.values():
            e[v.stageInfo.identifier] = v.stageStatus
        return e