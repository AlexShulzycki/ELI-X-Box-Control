import fastapi.websockets


class WebSocketAPI:
    """
    Handles websocket communication.
    This class will push data to the client, i.e. position updates from the controllers.
    """
    def __init__(self, wsmanager):
        self.wsmanager = wsmanager
        #self.axmanager = AxisManager(self.wsmanager)
        #self.stmanager = StageManager(self.wsmanager, self.axmanager)

    async def receive(self, msg, websocket: fastapi.websockets.WebSocket) -> None:
        """
        Receives and reacts to websocket messages
        :param msg: request parsed from json into a python object
        :param websocket: websocket which sent the request
        :return: none for now i guess
        """

        match msg["request"]:
            case "connectC884":
                pass
            case "ping":
                await websocket.send_json({"response":"ping"})
