from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class DeviceType(Enum):
    stage_linear = "stage_linear"
    stage_rotational = "stage_rotational"
    sensor = "sensor"

class Device(BaseModel):
    identifier: int = Field(description="Unique identifier for this device")
    configuration_id: int = Field(description="Which configuration this device belongs to")
    deviceType: DeviceType = Field(description="What kind of device this is")
    connected: bool = Field(description="Whether this device is connected", default=False)
    description: str = Field(description="Description of what this device is and/or does", default="")


class MotionStageDevice(Device):
    on_target: bool = Field(description="Whether this stage is on target", default=False)
    referenced: bool = Field(description="Whether this stage is referenced", default=False)

class LinearStageDevice(Device):
    deviceType = DeviceType.stage_linear
    position: float = Field(description="Position of this stage in millimeters", default=0)
    maximum: float = Field(description="The max range of this stage")

class RotationalStageDevice(Device):
    deviceType = DeviceType.stage_rotational
    angle: float = Field(description="Angle of this stage in degrees", default=0)

class SensorDevice(Device):
    deviceType = DeviceType.sensor
    units: str = Field(description="The units of what this sensor measures")

class Sensor(BaseModel):
    value: Any = Field(description="Value this sensor last measured")
    units: str = Field(description="The units of what this sensor measures")

class PowerSupplyDevice(Device):
    voltage: float = Field(description="Voltage")
    current: float = Field(description="Current")
    max_current: float = Field(description="Max current allowed")
    power: float = Field(description="Power")
    max_power: float = Field(description="Max power allowed")

class Action(BaseModel):
    name: str = Field(description="Name of this action")
    description: str = Field(description="Description of this action")
    value: type[float|bool|None] = Field(description="Input parameter for this action", default=None)

