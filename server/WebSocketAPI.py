from enum import Enum
from typing import Dict, Any

from fastapi import WebSocket
from pydantic import BaseModel, Field

from Interface import C884interface

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
    errortype: ErrTypes
    errormsg: str

    def __init__(self, errortype: ErrTypes, errormsg: str):
        super().__init__()
        self.response = "error"
        self.errortype = errortype
        self.errormsg = errormsg

class WebSocketAPI:
    """
    Handles websocket communication.
    This class will push updates to the client, i.e. position updates from the controllers.
    """
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def receive(self, msg: Req, websocket: WebSocket) -> None:
        """
        Receives and reacts to websocket messages
        :param msg: request parsed from json into a python object
        :param websocket: websocket which sent the request
        :return: none
        """
        # Prepopulate the response var as an unknown request error
        response: WsResponse = WsErrResponse(ErrTypes.unknown_request, f"Unknown request '{msg.request}'")
        try:
            match msg.request:
                case ReqTypes.ping:
                    response = WsResponse(response = "pong", data = {})
        except Exception as e:
            # We ran into something weird, send the error message and return
            await websocket.send_json(WsErrResponse(ErrTypes.unknown_request, str(e)))
            return

        # No exceptions, lets send the response
        await websocket.send_json(response)

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)