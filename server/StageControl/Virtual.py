from pydantic import Field, BaseModel

from .DataTypes import StageKind, StageInfo, StageStatus, ControllerInterface



class VirtualStage:
    def __init__(self, config: StageInfo):
        self.stageInfo = config
        self.stageStatus = StageStatus(connected=True, ready=True, position=config.minimum, ontarget=True)


class VirtualControllerInterface(ControllerInterface):

    def __init__(self):
        self.virtualstages: dict[int, VirtualStage] = {}

    def addStagesbyConfigs(self, configs: list[StageInfo]):
        for config in configs:
            self.virtualstages[config.identifier] = VirtualStage(config)

    @property
    def stages(self) -> list[int]:
        """Returns unique integer identifiers for each stage"""
        return list(self.virtualstages.keys())

    def moveTo(self, serial_number: int, position: float):
        """Move stage to position"""
        self.virtualstages[serial_number].stageStatus.position = position

    def onTarget(self, serial_numbers: list[int]) -> list[bool]:
        """Check if stages are on target"""
        return [True] * len(serial_numbers)

    def stageInfo(self, serial_numbers: list[int]) -> list[StageInfo]:
        """Return StageInfo objects for the given stages"""
        res = []
        for sn in serial_numbers:
            res.append(self.virtualstages[sn].stageInfo)
        return res

    def stageStatus(self, serial_numbers: list[int]) -> list[StageStatus]:
        """Return StageStatus objects for the given stages"""
        res = []
        for sn in serial_numbers:
            res.append(self.virtualstages[sn].stageStatus)
        return res
    def removeStage(self, serial_number: int):
        if serial_number in self.stages:
            self.virtualstages.pop(serial_number)
            return True
        else:
            return False