from __future__ import annotations

from enum import Enum
from typing import Any, ClassVar

from pydantic import BaseModel, Field, model_serializer
from pydantic_core.core_schema import SerializerFunctionWrapHandler


class Action(BaseModel):
    name: str = Field(description="Name of this action")
    description: str = Field(description="Description of this action")
    value: type[float|bool|None] = Field(description="Input parameter for this action", default=None)

class DeviceType(Enum):
    stage_linear = "stage_linear"
    stage_rotational = "stage_rotational"
    sensor = "sensor"

class Device(BaseModel):
    identifier: int = Field(description="Unique identifier for this device")
    configuration_id: int = Field(description="Which configuration this device belongs to")
    deviceType: ClassVar[DeviceType] = Field(description="What kind of device this is")
    connected: bool = Field(description="Whether this device is connected", default=False)
    description: str = Field(description="Description of what this device is and/or does", default="")
    actions: ClassVar[list[Action]] = Field(description="List of actions this device can perform", default=[])
    finished: bool = Field(description="Whether this device is finished with whatever it is doing, for example "
                                       "moving, or referencing", default=True)


class MotionStageDevice(Device):
    on_target: bool = Field(description="Whether this stage is on target", default=False)
    referenced: bool = Field(description="Whether this stage is referenced", default=False)
    actions = [
        Action(name="Move To", description="Move this stage to target", value=float),
        Action(name="Step By", description="Move this stage by the given amount", value=float),
        Action(name="Reference", description="Reference this stage")
    ]

class LinearStageDevice(MotionStageDevice):
    deviceType = DeviceType.stage_linear
    position: float = Field(description="Position of this stage in millimeters", default=0)
    maximum: float = Field(description="The max range of this stage", ge=0)

class RotationalStageDevice(MotionStageDevice):
    deviceType = DeviceType.stage_rotational
    angle: float = Field(description="Angle of this stage in degrees", default=0)

class SensorDevice(Device):
    deviceType = DeviceType.sensor
    value: Any = Field(description="Value this sensor last measured")
    units: str = Field(description="The units of what this sensor measures")

class Sensor(BaseModel):
    units: str = Field(description="The units of what this sensor measures")

class PowerSupplyDevice(Device):
    voltage: float = Field(description="Voltage")
    current: float = Field(description="Current")
    max_current: float = Field(description="Max current allowed")
    power: float = Field(description="Power")
    max_power: float = Field(description="Max power allowed")
    actions = [
        Action(name="enable_output", description="Enable or Disable power output", value=bool)
    ]


class Configuration(BaseModel):
    """
    Configuration object to be passed to a controller object. Must contain a unique SN field for identification of each
    configuration object, everything else is up to you.
    """
    ID: int = Field(description="Unique identifier for this configuration")
    ControllerType: ClassVar[str] = Field(description="What controller this configuration is for")


    # Force the inclusion of ControlleType in the serialization, otherwise it will not be included as it's a class var.
    @model_serializer(mode='wrap')
    def serialize_model(self, handler: SerializerFunctionWrapHandler) -> dict[str, object]:
        serialized = handler(self)
        serialized['ControllerType'] = self.ControllerType
        return serialized
