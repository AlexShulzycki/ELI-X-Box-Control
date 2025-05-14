from fastapi import WebSocket
from Interface import C884interface

class WebSocketAPI:
    """
    Handles websocket communication.
    This class will push data to the client, i.e. position updates from the controllers.
    """
    def __init__(self):
        #self.axmanager = AxisManager(self.wsmanager)
        #self.stmanager = StageManager(self.wsmanager, self.axmanager)
        self.active_connections: list[WebSocket] = []

    async def receive(self, msg, websocket: WebSocket) -> None:
        """
        Receives and reacts to websocket messages
        :param msg: request parsed from json into a python object
        :param websocket: websocket which sent the request
        :return: none
        """
        try:
            match msg["request"]:
                case "connectC884":
                    res = {"response": "updateC884", "data": C884interface.getUpdatedC884(msg["comport"])}
                    await self.broadcast(res)
                case "c884ontarget":
                    res = {"response": "ontargetPI", "ontarget": C884interface.onTarget(msg["comport"]), "comport": msg["comport"]}
                    await self.broadcast(res)
                case "c884moveto":
                    C884interface.moveTo(msg["comport"], msg["axis"], msg["target"])
                    res = {"response": "movingPI", "comport": msg["comport"], "axis": msg["axis"], "target": msg["target"]}
                    await self.broadcast(res)
                case "ping":
                    await websocket.send_json({"response":"ping"})
        except Exception as e:
            await websocket.send_json({"response": "error", "data": str(e)})

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)