from __future__ import annotations

from typing import Callable, Any


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
        # The following line is useful for debug,
        # it shows the path of each event up the chain
        #print(f"event at {self.host}", event)
        for sub in self.subs:
            if sub.datatypes.__contains__(type(event)):
                sub.event(event)

    def unsubscribe(self, sub: Subscription):
        self.subs.remove(sub)

    def patch_through_from(self, datatypes: list[type], target: EventAnnouncer):
        """
        Patch through events of this type from the target EventAnnouncer
        :param datatypes: Datatypes to forward
        :param target: target EventAnnouncer
        :return:
        """
        sub = target.subscribe(*datatypes)
        for datatype in datatypes:
            sub.deliverTo(datatype, self.event)
