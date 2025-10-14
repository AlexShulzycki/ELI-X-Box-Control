from typing import Any

from pydantic import Field

from .DataTypes import StageKind, StageStatus, ControllerInterface, updateResponse, \
    StageRemoved, EventAnnouncer, Configuration, StageInfo, ConfigurationUpdate, Notice


class VirtualStageInfo(Configuration):
    # identifier is now SN, minimum is hardwired to zero
    model: str = Field(description="Stage model, i.e. L-406.20DD10", examples=["L-406.20DD10", "Virtual Linear Stage"])
    kind: StageKind = Field(default=StageKind.linear, description="What kind of stage this is")
    maximum: float = Field(default=0, description="Maximum position, in mm.", ge=0)

    def toStageInfo(self) -> StageInfo:
        return StageInfo(
            model=self.model,
            identifier=self.SN,
            kind=self.kind,
            minimum= 0,
            maximum=self.maximum
        )

class VirtualSettings:

    def __init__(self):
        self.EventAnnouncer = EventAnnouncer(VirtualSettings, StageStatus, StageInfo, StageRemoved, Notice, ConfigurationUpdate)
        self._controllerStatuses = []
        self.virtualstages: dict[int, VirtualStage] = {}

    @property
    def currentConfiguration(self) -> list[VirtualStageInfo]:
        res = []
        for v in self.virtualstages.values():
            res.append(v.stageInfo)
        return res

    async def configurationChangeRequest(self, requests: list[VirtualStageInfo]) -> list[updateResponse]:
        res = []
        for request in requests:
            try:
                    self.virtualstages[request.SN] = VirtualStage(request)
                    res.append(updateResponse(
                        identifier=request.SN,
                        success=True,
                    ))
                    # success, send an event update
                    self.EventAnnouncer.event(self.virtualstages[request.SN].stageInfo.toStageInfo())
            except Exception as e:
                res.append(updateResponse(
                    identifier = request.SN,
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
        return VirtualStageInfo

    def getDataTypes(self):
        return [VirtualStageInfo, StageStatus]


class VirtualStage:
    def __init__(self, config: VirtualStageInfo):
        self.stageInfo = config
        self.stageStatus = StageStatus(identifier= config.SN, connected=True, ready=True, position=0, ontarget=True)


class VirtualControllerInterface(ControllerInterface):

    async def configurationChangeRequest(self, request: list[VirtualStageInfo]) -> list[updateResponse]:
        return await self.settings.configurationChangeRequest(request)

    async def removeConfiguration(self, id: int):
        return await self.settings.removeConfiguration(id)

    @property
    def configurationType(self):
        return VirtualStageInfo

    @property
    async def configurationSchema(self):
        schema =  self.settings.configurationFormat.model_json_schema()
        schema["title"] = "Virtual"
        return schema

    async def fullRefreshAllSettings(self):
        pass

    async def moveBy(self, identifier: int, step: float):
        self.settings.virtualstages[identifier].stageStatus.position += step
        self.settings.virtualstages[identifier].stageStatus.ontarget = True
        self.EventAnnouncer.event(self.stageStatus[identifier])

    def __init__(self):
        super().__init__()
        self._settings:VirtualSettings = VirtualSettings()
        # forward events
        sub = self.settings.EventAnnouncer.subscribe(StageInfo, StageRemoved)
        sub.deliverTo(StageInfo, self.EventAnnouncer.event)
        sub.deliverTo(StageRemoved, self.EventAnnouncer.event)

    @property
    def currentConfiguration(self):
        return self.settings.currentConfiguration

    @property
    def settings(self) -> VirtualSettings:
        return self._settings

    @property
    def name(self) -> str:
        return "Virtual"

    @property
    def stages(self) -> list[int]:
        """Returns unique integer identifiers for each stage"""
        return list(self.settings.virtualstages.keys())

    async def moveTo(self, serial_number: int, position: float):
        """Move stage to position"""
        self.settings.virtualstages[serial_number].stageStatus.position = position
        self.settings.virtualstages[serial_number].stageStatus.ontarget = True
        self.EventAnnouncer.event(self.stageStatus[serial_number])

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
            e[v.stageInfo.SN] = v.stageInfo.toStageInfo()
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
            e[v.stageInfo.SN] = v.stageStatus
        return e