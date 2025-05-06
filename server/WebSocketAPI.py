

class WebSocketAPI:
    """
    Handles websocket communication
    """
    def __init__(self, wsmanager):
        self.wsmanager = wsmanager
        #self.axmanager = AxisManager(self.wsmanager)
        #self.stmanager = StageManager(self.wsmanager, self.axmanager)

    def receive(self, msg: object, websocket) -> None:
        """
        Receives and reacts to websocket messages
        :param msg: request parsed from json into a python object
        :param websocket: websocket which sent the request
        :return: none for now i guess
        """
        print(msg)
        return

        match(request):
            case "connectC884":
                pass
            case "ping":
                self.wsmanager.send_msg_to("pong", websocket)