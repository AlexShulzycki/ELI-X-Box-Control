from __future__ import annotations

from pydantic import BaseModel, Field

from server.Devices import Device
from server.Devices.DataTypes import Configuration


class ConfigurationUpdate(BaseModel):
    """Update to the configuration state to be sent via websockets"""
    SN: int
    """Identifier of the configuration object"""
    message: str
    """Description that can be displayed to the user"""
    configuration: Configuration|None = None
    """New configuration state"""
    finished: bool = False
    """Whether something is still happening, and you should expect another
    ConfigurationUpdate soon"""
    error: bool = False
    """If this ConfigurationUpdate heralds bad news"""

class DeviceUpdate(BaseModel):
    """Update to the device state to be sent via websockets"""
    identifier: int = Field(description="Identifier of the device")
    state: Device


class updateResponse(BaseModel):
    """Response to a configuration change request"""
    identifier: int
    success: bool
    error: str|None = Field(default=None)


class Notice(BaseModel):
    """This is a class that can send any miscellaneous string up the chain"""
    identifier:int|None = Field(description="Identifier of the device this refers to. If not pertaining to a single device, set to None", default=None)
    message: str
