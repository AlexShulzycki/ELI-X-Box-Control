import asyncio
import json
from enum import Enum
from typing import Dict, Any

from fastapi import WebSocket
from pydantic import BaseModel, Field

from server.Interface import toplevelinterface
from server.StageControl.DataTypes import EventAnnouncer, StageStatus, StageInfo, StageRemoved, Notice, \
    ConfigurationUpdate, Configuration


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

class DeviceTypes(Enum):
    c884 = "pi_c884"
    smc5 = "standa_smc5"

class UpdateTypes(Enum):
    error_update = "error_update"
    motion_update = "motion_update"

class Update(BaseModel):
    event: UpdateTypes

class StageMotionStatus(BaseModel):
    device_type: DeviceTypes = Field(description="Device type", examples=[DeviceTypes.c884, DeviceTypes.smc5])
    position: list[float| None] = Field(description="Position of each stage in mm", examples=[[9.32], [1.4, None, 53.44]])
    on_target: list[bool| None] = Field(description="On target status for the stages", examples=[True, False, None, False])

class MotionUpdate(Update):
    event: UpdateTypes = UpdateTypes.motion_update
    stages: list[StageMotionStatus] = Field(default = [], description="List of StageMotionStatus objects")

class ErrorUpdate(Update):
    event: UpdateTypes = UpdateTypes.error_update
    errortype: ErrTypes = Field(description="Error type", examples=[ErrTypes.malformed_request], default=ErrTypes.other_error)
    errormsg: str = Field(default="Unknown error", description="Error message")





class WebSocketAPI:
    """
    Handles websocket communication.
    This class will push updates to the client, i.e. position updates from the controllers.
    """

    def __init__(self):
        self.active_connections: list[WebSocket] = []
        self.EA: EventAnnouncer = EventAnnouncer(WebSocketAPI, StageStatus)
        # Subscribe to stage status changes
        self.EA.patch_through_from([StageStatus, StageInfo, StageRemoved, Notice, ConfigurationUpdate], toplevelinterface.EventAnnouncer)
        sub = toplevelinterface.EventAnnouncer.subscribe(StageStatus, StageInfo, StageRemoved, Notice, ConfigurationUpdate)
        sub.deliverTo(StageStatus,self.broadcastStageStatus)
        sub.deliverTo(StageInfo,self.broadcastStageInfo)
        sub.deliverTo(StageRemoved, self.broadcastStageRemoved)
        sub.deliverTo(Notice, self.broadcastNotice)
        sub.deliverTo(ConfigurationUpdate, self.broadcastConfigurationUpdate)

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

    def broadcastStageRemoved(self, message: StageRemoved):
        asyncio.create_task(
            self.broadcast({
                "event": "StageRemoved",
                "data": message.model_dump_json()
            })
        )
    def broadcastStageStatus(self, message: StageStatus):
        asyncio.create_task(
            self.broadcast({
            "event": "StageStatus",
            "data": message.model_dump_json()
        }))

    def broadcastStageInfo(self, message: StageInfo):
        asyncio.create_task(self.broadcast({
            "event": "StageInfo",
            "data": message.model_dump_json()
        }))

    def broadcastNotice(self, message: Notice):
        asyncio.create_task(self.broadcast({
            "event": "Notice",
            "data": message.model_dump_json()
        }))

    def broadcastConfigurationUpdate(self, message: ConfigurationUpdate):

        # Because pydantic will only dump to the base class in nested objects, we need to do it manually
        if message.configuration is not None: # because we don't need to pass in a configuration
            config = message.configuration.model_dump() # this will dump subclasses properly
            message = message.model_dump() # pydantic says no I won't dump subclasses in properties
            message["configuration"] = config # so we say yes you will

        asyncio.create_task(self.broadcast({
            "event": "ConfigurationUpdate",
            "data": message
        }))

    async def broadcast(self, json: dict[str, str]):
        print(f"Broadcasting event {json} to {len(self.active_connections)} active clients")
        awaiters = []
        for connection in self.active_connections:
            awaiters.append(connection.send_json(json))
        await asyncio.gather(*awaiters)


websocketapi = WebSocketAPI()
