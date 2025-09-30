from __future__ import annotations

import time
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator
from pydantic_core.core_schema import FieldValidationInfo

from server.StageControl.DataTypes import StageStatus, StageInfo, EventAnnouncer, StageKind, \
    StageRemoved


class C884Settings(BaseModel):
    pass

class PIConnectionType(Enum):
    usb = "usb"
    rs232 = "rs232"
    network = "network"

class PIControllerModel(Enum):
    C884 = "C884"
    mock = "mock"

class PIStage(BaseModel):
    channel: int = Field(description="Which channel this stage is connected to")
    device:str = Field(description="Name of the stage, i.e. L-611.90AD", examples=['L-406.20DD10', 'NOSTAGE', 'L-611.90AD', 'NOSTAGE'])
    clo: bool = Field(description="Whether the stage is in closed loop operation")
    referenced: bool = Field(description="Whether the stage is referenced")
    min_max: tuple[float, float] = Field(description="Minimum and maximum travel range, in mm", examples=[[0, 200]])
    on_target: bool = Field(description="Whether the stage is on target")
    position: float = Field(description="Position of the stage, in mm", examples=[12.55, 100.27])


class PIConfiguration(BaseModel):
    """
    State of a single PI controller. Required: SN, model, connection_type (with additional rs232 fields if required)
    """
    SN: int = Field(description="Serial number of the controller")
    model: PIControllerModel = Field(description="Name of the model", examples=[PIControllerModel.C884])
    connection_type: PIConnectionType = Field(description="How the controller is connected")
    connected: bool = Field(default= False, examples=[True, False], description="If the controller is connected")
    channel_amount: int = Field(default= 0, examples=[0,4,6], description="Number of channels controller supports")
    ready: bool = Field(default= False, examples=[True, False], description="Whether the controller is ready")
    stages: dict[str,PIStage] = Field(default= None, description="List of stage objects containing all relevant information")
    error: str = Field(description="Error message. If no error, its an empty string", default="")
    baud_rate: int = Field(description="Baud rate of RS232 connection.", default=115200, examples=[115200])
    comport: int = Field(default = None, description="Comport for RS232 connection.")



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
        else: return value

    class Config:
        validate_assignment = True

class PIStageInfo(StageInfo):
    controllerSN: int  = Field(description="SN of controller controlling this stage")
    channel: int = Field(description="Which controller channel this stage is connected to")

    # the identifier is supposed to be (controller SN)(channel number) so we check this is true
    # I cant be bothered to do the math thing so we check using strings, sorry.
    @field_validator("controllerSN", mode="after")
    def validate_controllerSN(cls, value, info: FieldValidationInfo):
        if str(info.data["identifier"])[:-1] != str(value):
            raise ValueError(f"SN {value} doesnt match identifier")
        return value

    @field_validator("channel")
    def validate_channelSN(cls, value, info: FieldValidationInfo):
        if str(info.data["identifier"])[-1] != str(value):
            raise ValueError(f"SN {value} doesnt match identifier")
        return value

    class Config:
        validate_assignment = True

class PIController:
    #TODO Implement event announcer
    def __init__(self):
        self.EA = EventAnnouncer(StageStatus, StageInfo, StageRemoved)
        self._config = None


    async def updateFromConfig(self, status: PIConfiguration):
        raise NotImplementedError

    def shutdown_and_cleanup(self):
        raise NotImplementedError

    async def refreshFullStatus(self):
        """
        Refresh the entire status of the controller.
        """
        raise NotImplementedError

    async def refreshPosOnTarget(self):
        """
        Just like refreshFullStatus, but only refreshes position and ontarget status.
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
    def stageInfos(self) -> dict[int, PIStageInfo]:
        res = {}
        for stage in self.config.stages.values():
            # Check if valid stage
            if (stage == "NOSTAGE") or (not stage.referenced):
                continue

            res = PIStageInfo(
                controllerSN=self.config.SN,
                channel=stage.channel,
                model = stage.device,
                identifier =self.config.SN * 10 + (stage.channel + 1), # controller SN plus channel
                kind = StageKind.linear, #TODO UNHARDCODE
                minimum = stage.min_max[0],
                maximum = stage.min_max[1]
            )
            # if we are here, the stage exists
            res[res.identifier] = res


        return res


    @property
    def stageStatuses(self) -> dict[int, StageStatus]:
        res = {}
        for stage in self.config.stages.values():
            # Check if valid stage
            if (stage == "NOSTAGE") or (not stage.referenced):
                continue

            stat = (StageStatus(
                identifier =self.config.SN * 10 + (stage.channel + 1),
                connected = self.config.connected,
                ready = self.config.ready,
                position=stage.position,
                ontarget=stage.on_target
            ))
            res[stat.identifier] = stat
        return res

class MockPIController(PIController):
    """
    PI controller that's not real, used for testing, doesn't connect to anything, but acts like one.
    """

    def __init__(self):
        super().__init__()
        self.position = None
        self.on_target = None


    async def connect(self):
        time.sleep(0.1)
        self._config.connected = True

    async def reference(self, toreference):
        time.sleep(0.1)
        self._config.referenced = toreference

    async def load_stages(self, stages):
        time.sleep(0.1)
        if self.config.channel_amount != len(stages):
            # We redo the stages thing
            self._config.channel_amount = len(stages)
            self._config.stages = ["NOSTAGE"] * len(stages)
            self._config.position = [None] * len(stages)
            self._config.on_target = [None] * len(stages)
            self._config.clo = [None] * len(stages)
            self._config.min_max = [None] * len(stages)

        for i, stage in enumerate(stages):
            if stage == "NOSTAGE":
                continue
            else:
                self._config.stages[i] = stage
                self._config.min_max[i] = [0,0]
                self._config.position[i] = 0
                self.config.on_target[i] = False

        self._config.stages = stages

    async def enable_clo(self, clo):
        time.sleep(0.1)
        self._config.clo = clo

    async def updateFromConfig(self, config: PIConfiguration):
        # Double check that we have the correct config
        assert config.model == PIControllerModel.mock

        # Check if we are brand new
        if self.config is None:
            # ugly if then can't be bothered to streamline this
            if config.connection_type != PIConnectionType.rs232:
                self._config = PIConfiguration(
                    SN = config.SN,
                    model = config.model,
                    connection_type = config.connection_type,
                )
            else:
                self._config = PIConfiguration(
                    SN=config.SN,
                    model=config.model,
                    connection_type=config.connection_type,
                    comport=config.comport,
                    baud_rate=config.baud_rate)

        # Go through each parameter step by step
        if not self.config.connected and config.connected:
            #connect
            await self.connect()

        if config.stages != self.config.stages:
            await self.load_stages(config.stages)

        if config.clo != self.config.clo:
            await self.enable_clo(config.clo)

        if config.referenced != self.config.referenced:
            await self.reference(config.referenced)

        # TODO find a way to simulate this more closely
        self._config.ready = True

        # refresh full status after changing config
        await self.refreshFullStatus()

    def shutdown_and_cleanup(self):
        pass

    async def refreshFullStatus(self):
        # Send an info update, status is handled in pos on target
        for info in self.stageInfos.values():
            self.EA.event(info)

        # also refresh pos on target since this is a full refresh
        await self.refreshPosOnTarget()

    async def refreshPosOnTarget(self):
        # Send a status update
        for status in self.stageStatuses.values():
            self.EA.event(status)

    async def moveTo(self, channel:int, position: float):
        self._config.position[channel-1] = position
        self._config.on_target[channel-1] = True
        self.EA.event(self.stageStatuses[self.config.SN*10 +channel])

    async def moveBy(self, channel, step: float):
        self._config.position[channel-1] += step
        self._config.on_target[channel-1] = True
        self.EA.event(self.stageStatuses[self.config.SN*10 +channel])

    @property
    def config(self) -> PIConfiguration:
        return self._config
