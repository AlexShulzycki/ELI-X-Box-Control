from typing import Any

from pydantic import Field, BaseModel

from .DataTypes import StageKind, StageInfo, StageStatus, ControllerInterface, ControllerSettings


class VirtualSettings(ControllerSettings):

    def __init__(self):
        super().__init__()
        self.virtualstages: dict[int, VirtualStage] = {}

    @property
    def currentConfiguration(self) -> list[Any]:
        res = []
        for v in self.virtualstages.values():
            res.append(v)
        return res

    def configurationChangeRequest(self, requests: list[StageInfo]):
        for request in requests:
            if request.identifier not in self.virtualstages:
                self.virtualstages[request.identifier] = VirtualStage(request)
            else:
                raise Exception(f"Virtual Stage {request.identifier} already exists, use another identifier.")

    def removeConfiguration(self, identifier: int):
        if identifier in self.virtualstages.keys():
            self.virtualstages.pop(identifier)
            return True
        else:
            return False

    @property
    def configurationFormat(self):
        return StageInfo.model_json_schema()

    def getDataTypes(self):
        return [StageInfo, StageStatus]


class VirtualStage:
    def __init__(self, config: StageInfo):
        self.stageInfo = config
        self.stageStatus = StageStatus(identifier= config.identifier, connected=True, ready=True, position=config.minimum, ontarget=True)


class VirtualControllerInterface(ControllerInterface):

    def __init__(self):
        self.settings:VirtualSettings = VirtualSettings()
        super().__init__()

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

    def updateStageInfo(self, identifiers: list[int] = None):
        """Return StageInfo objects for the given stages"""
        # loop through I cant be bothered
        for v in self.settings.virtualstages.values():
            self.EventAnnouncer.event(v.stageInfo)
        return

    @property
    def stageInfo(self) -> dict[int, StageInfo]:
        e = {} # dunno why I called it e
        for v in self.settings.virtualstages.values():
            e[v.stageInfo.identifier] = v.stageInfo
        return e

    def updateStageStatus(self, identifiers: list[int] = None):
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