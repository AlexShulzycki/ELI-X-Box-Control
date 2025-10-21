from typing import Any

from pydantic import Field

from server.Devices import Device, LinearStageDevice, Configuration
#from server.Devices.DataTypes import StageStatus, StageRemoved, StageInfo
from server.Devices.Events import ConfigurationUpdate, updateResponse, Notice
from server.utils.EventAnnouncer import EventAnnouncer
from server.Interface import ControllerInterface


class VirtualStageConfig(Configuration):
    ControllerType = "Virtual"
    # stage is hardwired as linear for now. model is so far unnecessary and extra work for testing
    #model: str = Field(description="Stage model, i.e. L-406.20DD10", examples=["L-406.20DD10", "Virtual Linear Stage"])
    maximum: float = Field(default=0, description="Maximum position, in mm.", ge=0)

class VirtualStage:
    def __init__(self, config: VirtualStageConfig):
        self.identifier: int = config.ID
        self.maximum = None
        self.position = 0
        self.on_target = None
        self.updateFromConfig(config)

    def updateFromConfig(self, config: VirtualStageConfig):

        self.maximum = config.maximum
        self.on_target = True
        return updateResponse(
            identifier=self.identifier,
            success=True
        )


    @property
    def device(self) -> LinearStageDevice:
        return LinearStageDevice(
            identifier = self.identifier,
            maximum = self.maximum,
            position = self.position,
            on_target = self.on_target,
            referenced = True,
            configuration_id= self.identifier, # same as the device identifier, 1 device per config
            connected=True,
            description=f"Virtual linear stage, ID {self.identifier}"
            )
    @property
    def config(self) -> VirtualStageConfig:
        return VirtualStageConfig(
            ID = self.identifier,
            maximum = self.maximum,
        )

class VirtualInterface(ControllerInterface):


    @property
    def configurationPydanticModel(self):
        return VirtualStageConfig

    def __init__(self):
        super().__init__()
        self.stages: dict[int, VirtualStage] = {}


    @property
    def devices(self) -> list[Device]:
        res = []
        for stage in self.stages.values():
            res.append(stage.device)
        return res

    async def execute_action(self, identifier, action, value: None | bool | float | str) -> None:
        pass

    async def refresh_devices(self, ids:list[int]|None = None) -> None:
        pass

    @property
    def device_schemas(self) -> list[dict[str, Any]]:
        return [LinearStageDevice.model_json_schema()]

    @property
    def name(self) -> str:
        return "Virtual"

    async def configurationChangeRequest(self, request: list[VirtualStageConfig]) -> list[updateResponse]:
        res = []
        for req in request:
            if self.stages.__contains__(req.ID):
                res.append(self.stages[req.ID].updateFromConfig(req))
            else:
                self.stages[req.ID] = VirtualStage(req)
                res.append(self.stages[req.ID].updateFromConfig(req))
        return res

    async def removeConfiguration(self, ident: int) -> updateResponse:
        # if config exists, remove, else, say we failed
        if ident in self.stages:
            del self.stages[ident]
            return updateResponse(
                identifier=ident,
                success=True
            )
        else:
            return updateResponse(
                identifier=ident,
                success=False
            )

    @property
    async def configurationSchema(self) -> dict:
        schema =  VirtualStageConfig.model_json_schema()
        # remember to set the title
        schema["title"] = "Virtual"
        return schema

    @property
    def currentConfigurations(self) -> list[Configuration]:
        res = []
        for stage in self.stages.values():
            res.append(stage.config)
        return res

    async def refresh_configurations(self) -> None:
        pass