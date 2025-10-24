import asyncio
import json
from enum import Enum
from typing import Dict, Any

from fastapi import WebSocket
from pydantic import BaseModel, Field

import server.utils.EventAnnouncer
from server import toplevelinterface
from server.Devices import Configuration
from server.Devices.Events import ConfigurationUpdate, Notice, DeviceUpdate
from server.utils.EventAnnouncer import EventAnnouncer


class ReqTypes(Enum):
    """Enumerates request types for websocket connections"""
    ping = "ping"


class ErrTypes(Enum):
    """Enumeration of errors sent over WS"""
    malformed_request = "malformed_request"
    unknown_request = "unknown_request"
    other_error = "other_error"


class Req(BaseModel):
    """Websocket request from client"""
    request: ReqTypes


class WsResponse(BaseModel):
    """Websocket response to client"""
    response: str
    data: Dict[str, Any]


class WsErrResponse(WsResponse):
    """Websocket error response to client"""
    response: str = "error"
    errortype: ErrTypes
    errormsg: str






class WebSocketAPI:
    """
    Handles websocket communication.
    This class will push updates to the client, i.e. position updates from the controllers.
    """

    def __init__(self):
        self.active_connections: list[WebSocket] = []
        self.EA: EventAnnouncer = EventAnnouncer(WebSocketAPI, ConfigurationUpdate, DeviceUpdate)
        # Subscribe to stage status changes
        self.EA.patch_through_from(self.EA.availableDataTypes,
                                   server.toplevelinterface.EventAnnouncer)

        # handle deliveries
        sub = self.EA.subscribe(*self.EA.availableDataTypes)
        #sub.deliverTo(Notice, self.broadcastNotice)
        sub.deliverTo(ConfigurationUpdate, self.broadcastConfigurationUpdate)
        sub.deliverTo(DeviceUpdate, self.broadcastDeviceUpdate)
        #sub.deliverTo()

    async def receive(self, msg: Req, websocket: WebSocket) -> None:
        """
        Receives and reacts to websocket messages
        :param msg: request parsed from json into a python object
        :param websocket: websocket which sent the request
        :return: none
        """
        print(f"Received WS: {msg}")
        # Prepopulate the response var as an unknown request error
        response: WsResponse = WsErrResponse(errortype = ErrTypes.unknown_request, errormsg = f"Unknown request '{msg.request}'")
        try:
            match msg.request:
                case ReqTypes.ping:
                    response = WsResponse(response="pong", data={})
        except Exception as e:
            # We ran into something weird, send the error message and return
            await websocket.send_json(WsErrResponse(errortype= ErrTypes.unknown_request, errormsg= str(e)))
            return

        # No exceptions, lets send the response
        await websocket.send_json(response)

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    def broadcastNotice(self, message: Notice):
        asyncio.create_task(self.broadcast({
            "event": "Notice",
            "data": message.model_dump_json()
        }))

    def broadcastConfigurationUpdate(self, message: ConfigurationUpdate):

        # Because pydantic will only dump to the base class in nested objects, we need to do it manually
        if message.configuration is not None: # because we don't need to pass in a configuration
            config = message.configuration.model_dump_json() # this will dump subclasses properly
            message = message.model_dump_json() # pydantic says no I won't dump subclasses in properties

            # force-feed into dicts
            message = json.loads(message)
            config = json.loads(config)

            message["configuration"] = config # we now have a proper json-ready dict

        else:
            # just do a regular JSON serialization
            message = json.loads(message.model_dump_json())

        asyncio.create_task(self.broadcast({
            "event": "ConfigurationUpdate",
            "data": message
        }))

    def broadcastDeviceUpdate(self, message: DeviceUpdate):
        asyncio.create_task(self.broadcast({
            "event": "DeviceUpdate",
            "data": message.model_dump()
        }))

    async def broadcast(self, json: dict[str, str]):
        #print(f"Broadcasting event {json} to {len(self.active_connections)} active clients")
        awaiters = []
        for connection in self.active_connections:
            awaiters.append(connection.send_json(json))
        await asyncio.gather(*awaiters)


websocketapi = WebSocketAPI()
