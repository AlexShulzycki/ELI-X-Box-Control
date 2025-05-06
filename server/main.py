from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import WebSocketAPI
app = FastAPI()

@app.get("/")
async def root():
    """
    Serves UI
    :return: The UI
    """
    return {"message": "Hello"}


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_msg_to(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


wsmanager = ConnectionManager()
wsAPI = WebSocketAPI.WebSocketAPI(wsmanager)

#AxisManager = StageControl.Controller.AxisManager(wsmanager)
#StageManager = StageControl.Controller.StageManager(wsmanager, AxisManager)


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await wsmanager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            wsAPI.receive(data, websocket)
    except WebSocketDisconnect:
        wsmanager.disconnect(websocket)
        await wsmanager.broadcast(f"Client #{client_id} left the chat")

