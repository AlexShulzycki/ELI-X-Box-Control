from __future__ import annotations

from enum import Enum
from typing import Any, Callable

from pydantic import BaseModel, Field, field_validator, model_validator
from pydantic_core.core_schema import FieldValidationInfo


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


class EventAnnouncer:
    def __init__(self, *availableDataTypes: type):
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
        for sub in self.subs:
            if sub.datatypes.__contains__(type(event)):
                sub.event(event)

    def unsubscribe(self, sub: Subscription):
        self.subs.remove(sub)


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




class ControllerInterface:
    """
    Base class of controller interfaces. Make sure you pass on any updates to the event announcer.

    """

    def __init__(self):
        self.EventAnnouncer = EventAnnouncer(StageStatus, StageInfo)

    @property
    def stages(self) -> list[int]:
        """Returns unique integer identifiers for each stage"""
        raise NotImplementedError

    def moveTo(self, identifier: int, position: float):
        """Move stage to position"""
        raise NotImplementedError

    @property
    def stageInfo(self) -> dict[int, StageInfo]:
        """Returns StageInfo of connected stages"""
        raise NotImplementedError

    def updateStageInfo(self, identifiers: list[int] = None):
        """Updates StageInfo for the given stages or all if identifier list is empty.
        MUST UPDATE EVENTANNOUNCER"""
        raise NotImplementedError

    @property
    def stageStatus(self) -> dict[int, StageStatus]:
        """Return StageStatus objects for the given stages"""
        raise NotImplementedError

    def updateStageStatus(self, identifiers: list[int] = None):
        """Updates stageStatus for the given stages or all if identifier list is empty.
        MUST UPDATE EVENTANNOUNCER"""
        raise NotImplementedError

    def addStagesByConfigs(self, configs: list[Any]):
        raise NotImplementedError

    def removeStage(self, identifier: int) -> bool:
        """
        Removes the given stage, i.e. disconnects it and all related stages
        :param identifier: identifier of the stage to remove
        :return: Whether the stage was removed successfully
        """
        raise NotImplementedError



class ControllerSettings:

    def __init__(self):
        self.EventAnnouncer = EventAnnouncer(*self.getDataTypes())
        self._controllerStatuses = []
        pass

    @property
    def controllerStatuses(self) -> list[BaseModel]:
        """Send over a list of status objects specific for the controller.
        These status objects should describe all that is going on with the
        controller(s)"""
        return self._controllerStatuses

    def getDataTypes(self) -> list[type]:
        """ Some way of sending over the formatting of the settings """
        raise NotImplementedError

    async def configurationChangeRequest(self, request: Any):
        """
        Upon receiving a controller status object, tries to turn it into reality.
        :param request: controller status object, same as from controllerStatuses
        :return: Either none, or raise an error
        """
        raise NotImplementedError

    @property
    def stageStatus(self) -> dict[int, StageStatus]:
        """
        Returns StageStatus objects for configured stages.
        :return:
        """
        raise NotImplementedError

    @property
    def stageInfo(self) -> dict[int, StageInfo]:
        """
        Returns StageInfo objects for configured stages.
        :return:
        """
        raise NotImplementedError

