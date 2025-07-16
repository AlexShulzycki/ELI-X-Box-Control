from pydantic import Field, BaseModel

from .DataTypes import StageKind, StageInfo, StageStatus, ControllerInterface



class VirtualStage:
    def __init__(self, config: StageInfo):
        self.stageInfo = config
        self.stageStatus = StageStatus(identifier= config.identifier, connected=True, ready=True, position=config.minimum, ontarget=True)


class VirtualControllerInterface(ControllerInterface):

    def __init__(self):
        self.virtualstages: dict[int, VirtualStage] = {}
        super().__init__()

    def addStagesByConfigs(self, configs: list[StageInfo]):
        for config in configs:
            self.virtualstages[config.identifier] = VirtualStage(config)

    @property
    def stages(self) -> list[int]:
        """Returns unique integer identifiers for each stage"""
        return list(self.virtualstages.keys())

    def moveTo(self, serial_number: int, position: float):
        """Move stage to position"""
        self.virtualstages[serial_number].stageStatus.position = position
        self.virtualstages[serial_number].stageStatus.ontarget = True

    def updateStageInfo(self, identifiers: list[int] = None):
        """Return StageInfo objects for the given stages"""
        # loop through I cant be bothered
        for v in self.virtualstages.values():
            self.EventAnnouncer.event(v.stageInfo)
        return

    @property
    def stageInfo(self):
        e = {} # dunno why I called it e
        for v in self.virtualstages.values():
            e[v.stageInfo.identifier] = v.stageInfo
        return e

    def updateStageStatus(self, identifiers: list[int] = None):
        # loop through I cant be bothered
        for v in self.virtualstages.values():
            self.EventAnnouncer.event(v.stageStatus)
        return

    @property
    def stageStatus(self):
        """Return StageStatus objects for the given stages"""
        e = {}  # dunno why I called it e
        for v in self.virtualstages.values():
            e[v.stageInfo.identifier] = v.stageStatus
        return e

    def removeStage(self, serial_number: int):
        if serial_number in self.stages:
            self.virtualstages.pop(serial_number)
            return True
        else:
            return False