from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator

from server.StageControl.DataTypes import ControllerSettings, StageStatus, StageInfo


class C884Settings(BaseModel):
    pass

class PIConnectionType(Enum):
    usb = "usb"
    rs232 = "rs232"
    network = "network"

class PIControllerStatus(BaseModel):
    SN: int = Field(description="Serial number of the controller")
    connection_type: PIConnectionType = Field(description="How the controller is connected")
    connected: bool = Field(examples=[True, False], description="If the controller is connected")
    channel_amount: int = Field(examples=[0], description="Number of channels controller supports")
    ready: bool = Field(examples=[True, False], description="Whether the controller is ready")
    referenced: list[bool] = Field(examples=[[True, False, False, False]],
                                   description="Whether each axis is referenced")
    clo: list[bool] = Field(examples=[[True, False, True, False]],
                            description="Whether each axis is in closed loop operation, i.e. if its turned on")
    stages: list[str] = Field(default=["NOSTAGE", "NOSTAGE", "NOSTAGE", "NOSTAGE"], min_length=4,
                              examples=[['L-406.20DD10', 'NOSTAGE', 'L-611.90AD', 'NOSTAGE']])
    """Array of 4 devices connected on the controller, in order from channel 1 to 4, or 6. If no stage is
        present, "NOSTAGE" is required. Example: Channel 1 and 3 are connected: ['L-406.20DD10','NOSTAGE', 'L-611.90AD',
         'NOSTAGE']"""
    error: str = Field(description="Error message. If no error, its an empty string")
    baud_rate: int = Field(default=None, description="Baud rate of RS232 connection.")
    comport: int = Field(default = None, description="Comport for RS232 connection.")

    @field_validator("referenced", "clo", "stages")
    def validate_channel_amounts(self, value):
        if self.channel_amount != len(value):
            raise ValueError("Needs to match number of channels")
        return value

    @field_validator("connection_type")
    def validate_required_fields(self, value):
        if value is PIConnectionType.rs232:
            if self.baud_rate is None or self.comport is None:
                raise ValueError("Baud rate and comport must be specified for an RS232 connection")

        return value

class PIStageInfo(StageInfo):
    controllerSN: int  = Field(description="SN of controller controlling this stage")
    channel: int = Field(description="Which controller channel this stage is connected to")


    # the identifier is supposed to be (controller SN)(channel number) so we check this is true
    # I cant be bothered to do the math thing so we check using strings, sorry.
    @field_validator("controllerSN")
    def validate_controllerSN(cls, value):
        if str(cls.identifier)[:-1] != str(value):
            raise ValueError(f"SN {value} doesnt match identifier")
        return value

    @field_validator("channel")
    def validate_controllerSN(cls, value):
        if str(cls.identifier)[-1] != str(value):
            raise ValueError(f"SN {value} doesnt match identifier")
        return value


class PISettings(ControllerSettings):

    def __init__(self):
        ControllerSettings.__init__(self)
        # type hint, this is where we store controller statuses
        self._controllerStatuses: list[PIControllerStatus]

    async def configurationChangeRequest(self, request: PIControllerStatus):
        """
        Tries to turn the desired state into reality.
        :param request: A PIController status.
        :return:
        """
        pass



    def getDataTypes(self) -> list[type]:
        return [PIStageInfo, PIControllerStatus]


    @property
    def stageStatus(self) -> dict[int, StageStatus]:
        raise NotImplementedError

    @property
    def stageInfo(self) -> dict[int, PIStageInfo]:
        raise NotImplementedError