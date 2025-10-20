from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field, field_validator, model_validator
from pydantic_core.core_schema import FieldValidationInfo

class Configuration(BaseModel):
    """
    Configuration object to be passed to a controller object. Must contain a unique SN field for identification of each
    configuration object, everything else is up to you.
    """
    ID: int = Field(description="Unique identifier for this configuration")


class StageKind(Enum):
    rotational = "rotational"
    linear = "linear"


class StageInfo(BaseModel):
    """
    StageInfo contains configuration information about the stage, i.e. model, type, minmax.
    This data structure is extended for individual implementations for different brands, and
    more information can be put in here as needed.
    """
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
    """
    Stage Status contains basic information about the state of the stage, i.e. position and
    ontarget status.
    """
    identifier: int = Field(description='Unique identifier for the stage')
    connected: bool = Field(default=False, description="Whether the stage is connected.")
    ready: bool = Field(default=False, description="Whether the stage is ready or not.")
    position: float = Field(default=0.0, description="Position of the stage in mm.")
    ontarget: bool = Field(default=False, description="Whether the stage is on target.")

class StageRemoved(BaseModel):
    """Indicates that the stage has been removed."""
    identifier: int = Field(description='Unique identifier for the stage')


