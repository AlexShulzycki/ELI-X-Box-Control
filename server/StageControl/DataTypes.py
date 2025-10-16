from __future__ import annotations

import glob
import sys
from enum import Enum
from typing import Any, Callable

import serial
from pydantic import BaseModel, Field, field_validator, model_validator
from pydantic_core.core_schema import FieldValidationInfo

class Configuration(BaseModel):
    """
    Configuration object to be passed to a controller object. Must contain a unique SN field for identification of each
    configuration object, everything else is up to you.
    """
    SN: int = Field(description="Unique identifier for this configuration")

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

class Notice(BaseModel):
    """This is a class that can send any miscellaneous string up the chain"""
    identifier:int = None
    message: str

class ConfigurationUpdate(BaseModel):
    """Update to the configuration state"""
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

class ControllerInterface:
    """
    Base class of controller interfaces. Make sure you pass on any updates to the event announcer.

    """

    def __init__(self):
        self.EventAnnouncer = EventAnnouncer(ControllerInterface, StageStatus, StageInfo, StageRemoved, Notice, ConfigurationUpdate)

    @property
    def stages(self) -> list[int]:
        """Returns unique integer identifiers for each stage"""
        raise NotImplementedError

    async def moveTo(self, identifier: int, position: float):
        """Move stage to position"""
        raise NotImplementedError

    async def moveBy(self, identifier: int, step: float):
        """Move stage by offset"""
        raise NotImplementedError

    @property
    def stageInfo(self) -> dict[int, StageInfo]:
        """Returns StageInfo of connected stages"""
        raise NotImplementedError

    async def updateStageInfo(self, identifiers: list[int] = None):
        """Updates StageInfo for the given stages or all if identifier list is empty"""
        raise NotImplementedError

    @property
    def stageStatus(self) -> dict[int, StageStatus]:
        """Return StageStatus objects for the given stages"""
        raise NotImplementedError

    async def updateStageStatus(self, identifiers: list[int] = None):
        """Updates stageStatus for the given stages or all if identifier list is empty."""
        raise NotImplementedError

    @property
    def name(self) -> str:
        raise NotImplementedError

    async def configurationChangeRequest(self, request: list[Configuration]) -> list[updateResponse]:
        """
        Upon receiving a configuration object, tries to turn it into reality.
        :param request: configuration status object, same as from currentConfiguration
        :return: Either none, or raise an error
        """
        raise NotImplementedError

    async def removeConfiguration(self, id: int):
        """
        Remove a configuration. This can mean a controller, stage, whatever
        :param id: some kind of id to differentiate it, doesn't need to be a stage identifier.
        :return:
        """
        raise NotImplementedError

    @property
    def configurationType(self) -> type[Configuration]:
        raise NotImplementedError

    @property
    async def configurationSchema(self) -> dict:
        """
        Return the configuration object json schema
        :return:
        """
        raise NotImplementedError

    @property
    def currentConfiguration(self) -> list[Configuration]:
        raise NotImplementedError

    async def fullRefreshAllSettings(self):
        raise NotImplementedError

    async def is_configuration_configured(self, identifiers: list[int]) -> list[int]:
        """
         If the configuration change function does something that has to be checked again,
          i.e. if the stages have not yet finished referencing, then it is refreshed in this function,
          then if the action is completed, i.e. stages finished referencing, we return true. Otherwise,
          we return false and the server will query this function again after a short delay. Any ConfingurationUpdate
          events need to be sent here to update the UI. This function purely exists to allow the server to
          query this function when the need exists.
        :return: List of identifiers we need to check again
        """
        # return [] by default, override this in the individual interface implementations.
        return []

class updateResponse(BaseModel):
    identifier: int
    success: bool
    error: str|None = Field(default=None)

def getComPorts() -> list[int]:
    """
    Lists serial port names. Stolen from https://stackoverflow.com/a/14224477
    :raises EnvironmentError:
        On unsupported or unknown platforms
    :returns:
        A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(int(port[3:]))  # only return the com port number
        except (OSError, serial.SerialException):
            pass
    return result




class Subscription:

    def __init__(self, ea: EventAnnouncer, datatypes: list[type]):
        self.announcer = ea
        """EventAnnouncer we are subscribed to"""
        self.datatypes = datatypes
        """Supported datatypes"""
        self.deliveries: dict[type, list[Callable[[Any], None]]] = {}
        """Dict of data type -> list of callables"""

    def deliverTo(self, datatype:type, destination: Callable[[Any], None]):
        """
        Tell the subscription where to deliver received data
        :param datatype: Which datatype we want to receive
        :param destination: Function to call with the data
        :return: None
        """
        # Check that we serve this datatype
        if not self.datatypes.__contains__(datatype):
            raise Exception(f"Data type {datatype} is not delivered here")

        # Check if this key has been initialized, otherwise give it an empty list
        if self.deliveries.get(datatype) is None:
            self.deliveries[datatype] = []

        # Check if already registered
        if self.deliveries.get(datatype).__contains__(destination):
            print(f"delivery of {datatype} to {destination} is already registered")
            return

        # Register for deliveries
        self.deliveries[datatype].append(destination)

    def event(self, event: Any):
        """Calls relevant functions on receiving event"""

        # Check if delivery array exists or is empty
        if self.deliveries.get(type(event)) is None or len(self.deliveries.get(type(event))) == 0:
            print(f"No function is currently receiving {type(event)}")
            return

        # Deliver the package
        for func in self.deliveries.get(type(event)):
            func(event)

    def unsubscribe(self):
        self.announcer.unsubscribe(self)

class EventAnnouncer:
    def __init__(self, host: type|str,  *availableDataTypes: type):
        self.host = host
        """Information about the object hosting this EventAnnouncer, can be a type or a string. Useful for debugging"""
        self.subs: list[Subscription] = []
        self.availableDataTypes: list[type] = list(availableDataTypes)

    def subscribe(self, *datatypes: type) -> Subscription:
        """Subscribe to events, pass in the data type you want to get"""

        # Check that we have the requested data types
        for datatype in datatypes:
            if not self.availableDataTypes.__contains__(datatype):
                raise Exception(f"Data type {datatype} is not served here")

        # All good, add the subscription
        sub = Subscription(self, list(datatypes))
        self.subs.append(sub)
        return sub

    def event(self, event: Any):
        """Receive an event, send it to relevant subscribers"""
        #print(f"event at {self.host}", event) useful for debug
        for sub in self.subs:
            if sub.datatypes.__contains__(type(event)):
                sub.event(event)

    def unsubscribe(self, sub: Subscription):
        self.subs.remove(sub)

    def patch_through_from(self, datatypes: list[type], target: EventAnnouncer):
        """
        Patch through events of this type to the target EventAnnouncer
        :param datatypes: Datatypes to forward
        :param target: target EventAnnouncer
        :return:
        """
        sub = target.subscribe(*datatypes)
        for datatype in datatypes:
            sub.deliverTo(datatype, self.event)
