from enum import Enum
from typing import Coroutine, Any

from pydantic import BaseModel, Field, field_validator


class StageKind(Enum):
    rotational = "rotational"
    linear = "linear"


class StageInfo(BaseModel):
    identifier: int = Field(description='Unique identifier for the stage')
    kind: StageKind = Field(default=False, description="What kind of stage this is")
    minimum: float = Field(default=0, description="Minimum position, in mm.", ge=0)
    maximum: float = Field(description="Maximum position, in mm.", ge=0)

    # Validate that linear stages must have minimums and maximums
    @field_validator("minimum", "maximum")
    def isMinMaxNeeded(cls, v, values):
        if values["kind"] == StageKind.linear and v is None:
            raise ValueError("Linear stage needs minimum and maximum")


class ControllerInterface():
    """Base class of controller interfaces"""

    @property
    def stages(self) -> [int]:
        """Returns unique integer identifiers for each stage"""
        raise NotImplementedError

    def moveTo(self, serial_number: int, position: float):
        """Move stage to position"""
        raise NotImplementedError

    def onTarget(self, serial_numbers: [int]) -> list[bool]:
        """Check if stages are on target"""
        raise NotImplementedError

    def stageInfo(self, serial_numbers: [int]) -> list[StageInfo]:
        """Return StageInfo objects for the given stages"""
        raise NotImplementedError
