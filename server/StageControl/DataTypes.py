from enum import Enum

from pydantic import BaseModel, Field, field_validator, model_validator
from pydantic_core.core_schema import FieldValidationInfo


class StageKind(Enum):
    rotational = "rotational"
    linear = "linear"


class StageInfo(BaseModel):
    model: str = Field(description="Stage model, i.e. L-406.20DD10", examples=["L-406.20DD10", "Virtual Linear Stage"])
    identifier: int = Field(description='Unique identifier for the stage')
    kind: StageKind = Field(default=StageKind.linear, description="What kind of stage this is")
    minimum: float = Field(default=0, description="Minimum position, in mm.", ge=0)
    maximum: float = Field(default=0, description="Maximum position, in mm.", ge=0)

    # Validate that linear stages must have minimums and maximums
    @field_validator("minimum", "maximum")
    def isMinMaxNeeded(cls, v, info: FieldValidationInfo):
        if info.data["kind"] == StageKind.linear and v is None:
            raise ValueError("Linear stage needs minimum and maximum")
        return v

    @model_validator(mode='after')
    def minsmallerthanmax(self):
        if self.minimum > self.maximum:
            raise ValueError("Minimum position must be smaller or equal to maximum position")
        return self

class StageStatus(BaseModel):
    connected: bool = Field(default=False, description="Whether the stage is connected.")
    ready: bool = Field(default=False, description="Whether the stage is ready or not.")
    position: float = Field(default=0.0, description="Position of the stage in mm.")
    ontarget: bool = Field(default=False, description="Whether the stage is on target.")


class ControllerInterface:
    """Base class of controller interfaces"""

    @property
    def stages(self) -> list[int]:
        """Returns unique integer identifiers for each stage"""
        raise NotImplementedError

    def moveTo(self, serial_number: int, position: float):
        """Move stage to position"""
        raise NotImplementedError

    def onTarget(self, serial_numbers: list[int]) -> list[bool]:
        """Check if stages are on target"""
        raise NotImplementedError

    def stageInfo(self, serial_numbers: list[int]) -> list[StageInfo]:
        """Return StageInfo objects for the given stages"""
        raise NotImplementedError

    def stageStatus(self, serial_numbers: list[int]) -> list[StageStatus]:
        """Return StageStatus objects for the given stages"""
        raise NotImplementedError