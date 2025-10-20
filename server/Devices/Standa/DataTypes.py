from __future__ import annotations
from pydantic import BaseModel, Field
from server.Devices.DataTypes import StageKind


class StandaStage(BaseModel):
    Name: str
    Calibration: float = Field(description="Calibration value, i.e. how much (in mm) is one step")
    MinMax: tuple[float, float] = Field(description="Minimum and maximum range in mm")
    Kind: StageKind = Field(description="Linear or Rotational")

    class Config:
        arbitrary_types_allowed = True


class StandaConfiguration(BaseModel):
    SN: int
    model: str
    min_max: tuple[float, float]
    connected: bool = False
    homed: bool = False
    ontarget: bool = False
    position: float = 0


    class Config:
        arbitrary_types_allowed = True
