from __future__ import annotations

from enum import Enum
from typing import Any, Coroutine, Awaitable

from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
from pydantic.json_schema import DEFAULT_REF_TEMPLATE, GenerateJsonSchema, JsonSchemaMode
from pydantic_core.core_schema import FieldValidationInfo

from server.Settings import SettingsVault
from server.Devices.DataTypes import StageStatus, StageInfo, StageKind, \
    StageRemoved
from server.Devices import Configuration, Device, LinearStageDevice, RotationalStageDevice, MotionStageDevice
from server.Devices.Events import ConfigurationUpdate, Notice, ActionRequest
from server.utils.EventAnnouncer import EventAnnouncer


class C884Settings(BaseModel):
    pass


class PIConnectionType(str, Enum):
    usb = "usb"
    rs232 = "rs232"
    network = "network"


class PIControllerModel(str, Enum):
    C884 = "C884"
    mock = "mock"


class PIStage(BaseModel):
    channel: int = Field(description="Which channel this stage is connected to", examples=[1, 2, 3])
    device: str = Field(description="Name of the stage, i.e. L-611.90AD",
                        examples=['L-406.20DD10', 'NOSTAGE', 'L-611.90AD', 'NOSTAGE'])
    clo: bool = Field(default=False, description="Whether the stage is in closed loop operation")
    referenced: bool = Field(default=False, description="Whether the stage is referenced")
    min_max: list[float] = Field(default=[0, 500], description="Minimum and maximum travel range, in mm",
                                 examples=[[0, 200]], min_length=2, max_length=2, json_schema_extra={"readOnly": True})
    on_target: bool = Field(default=False, description="Whether the stage is on target",
                            json_schema_extra={"readOnly": True})
    position: float = Field(default=0, description="Position of the stage, in mm", examples=[12.55, 100.27],
                            json_schema_extra={"readOnly": True})
    kind: StageKind = Field(default=StageKind.linear, json_schema_extra={"readOnly": True})

    model_config = ConfigDict(
        validate_assignment=True,
        json_schema_extra={
            'title': 'PI Stage',
        }
    )


class PIConfiguration(Configuration):
    """
    State of a single PI controller. Required: SN, model, connection_type (with additional rs232 fields if required)
    """
    ID: int = Field(description="Serial number of the controller", title="Serial number of the controller")
    model: PIControllerModel = Field(description="Model of the PI controller", title="Model",
                                     examples=[PIControllerModel.C884])
    connection_type: PIConnectionType = Field(description="How the controller is connected",
                                              examples=[PIConnectionType.rs232], title="Connection type")
    connected: bool = Field(default=False, examples=[True, False], description="If the controller is connected",
                            json_schema_extra={"readOnly": True})
    channel_amount: int = Field(default=0, examples=[0, 4, 6], description="Number of channels controller supports",
                                json_schema_extra={"readOnly": True})
    ready: bool = Field(default=False, examples=[True, False], description="Whether the controller is ready",
                        json_schema_extra={"readOnly": True})
    stages: dict[str, PIStage] = Field(default={},
                                       description="Dict of stage objects containing all relevant information")
    error: str = Field(description="Error message. If no error, its an empty string", default="",
                       json_schema_extra={"readOnly": True})
    baud_rate: int = Field(description="Baud rate of RS232 connection.", default=115200, examples=[115200])
    comport: int = Field(description="Comport for RS232 connection.", default=0)

    @model_validator(mode="after")
    def validate_rs232(self):
        if self.connection_type is PIConnectionType.rs232:
            if self.comport is None:
                raise ValueError("Comport must be specified for an RS232 connection")

        return self

    @field_validator("ready")
    def not_ready_if_disconnected(cls, value, info: FieldValidationInfo):
        if not info.data["connected"]:
            return False
        else:
            return value

    class Config:
        validate_assignment = True,
        json_schema_extra = {
            'title': 'PI',
        }

    def toPIAPI(self) -> PIAPIConfig:
        """Converts this configuration to a PIAPIConfig. What it does is convert the dict of stages
        into a list of stages, so that it plays well with json schemas. We also """
        stages_dict = self.stages
        stages_list = []
        for stage in stages_dict.values():
            stages_list.append(stage)

        dump = self.model_dump()
        dump["stages"] = stages_list
        print(dump)
        return PIAPIConfig(**dump)


class PIController:
    def __init__(self):
        self.EA = EventAnnouncer(PIController, StageStatus, StageInfo, StageRemoved, Notice, ConfigurationUpdate)
        self._config = None
        self.SV = SettingsVault()

    async def updateFromConfig(self, status: PIConfiguration):
        raise NotImplementedError

    def shutdown_and_cleanup(self):
        raise NotImplementedError

    async def refreshFullStatus(self):
        """
        Refresh the entire status of the controller.
        """
        raise NotImplementedError

    async def refreshDevices(self):
        """
        Just like refreshFullStatus, but only refreshes relevant device information, i.e., ontarget, position, referenced.
        """
        raise NotImplementedError

    async def moveTo(self, channel, position: float):
        raise NotImplementedError

    async def moveBy(self, channel, step):
        raise NotImplementedError

    @property
    def config(self) -> PIConfiguration:
        """
        Construct and return a status object for this controller, WITHOUT asking the controller.
        """
        raise NotImplementedError

    @property
    def stages(self) -> list[PIStage]:
        res = []
        for stage in self.config.stages.values():
            res.append(stage)
        return res

    @property
    def devices(self) -> dict[int, Device]:
        res = {}
        for stage in self.config.stages.values():
            # Skip if NOSTAGE TODO check if necessary
            if stage.device == "NOSTAGE":
                continue
            identifier = self.config.ID*10 + stage.channel
            if stage.kind == StageKind.linear:
                res[stage.channel] = LinearStageDevice(
                    identifier=identifier,
                    configuration_id=self.config.ID,
                    maximum=stage.min_max[1],
                    position=stage.position,
                    on_target=stage.on_target,
                    referenced=stage.referenced
                )
            elif stage.kind == StageKind.rotational:
                res[stage.channel] = RotationalStageDevice(
                    identifier=identifier,
                    configuration_id=self.config.ID,
                    angle= stage.position,
                    on_target=stage.on_target,
                    referenced=stage.referenced
                )
        return res

    @staticmethod
    def fetchPIStageData(name: str, settings: object):
        """
        Look into the readonly settings if we have a stage of this name
        :param name: name of the stage, i.e. L406.20DD10
        :param settings: the settings dict loaded from disk
        :return: dict from the settings, {type: linear/rotational}
        """
        if settings.__contains__(name):
            return settings[name]
        else:
            raise Exception(f"Stage {name} not found in settings")

    async def is_configuration_configured(self) -> tuple[int, bool]:
        raise NotImplementedError

    def execute_action(self, action: ActionRequest):
        # find the stage
        cntrl_id, channel = self.deconstruct_SN_Channel(action.device_id)
        # do the action
        if action.action_name == "Move To":
            self.moveTo(channel, action.value)
        elif action.action_name == "Step By":
            self.moveBy(channel, action.value)
        else:
            raise Exception(f"Action {action.action_name} not recognized")

    @staticmethod
    def deconstruct_SN_Channel(sn_channel):
        """
        Extracts the channel and serial number from a unique serial-number-channel identifier
        :param sn_channel: serial number with the channel glued to the end
        :return: serial number and channel, separately!
        """
        channel: int = sn_channel % 10  # modulo 10 gives last digit
        sn: int = int((sn_channel - channel) / 10)  # minus channel, divide by 10 to get rid of 0
        return sn, channel

class PIAPIConfig(PIConfiguration):
    """This is a version of PIConfiguration that works nicely with JSON schemas. The
    difference is that it uses a list instead of a dict for storing PIStage objects."""
    stages: list[PIStage] = Field(default=[])

    def toPIConfig(self) -> PIConfiguration:
        """Convert this to a PIConfiguration"""
        stages_dict = {}
        # Iterate through stages, turn it from a list into a dict
        for stage in self.stages:
            # We use the channel number as a key. The key is in string format so we convert
            stages_dict[str(stage.channel)] = stage

        dump = self.model_dump()
        dump["stages"] = stages_dict
        return PIConfiguration(**dump)

