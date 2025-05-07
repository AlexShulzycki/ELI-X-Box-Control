from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import WebSocketAPI
import SettingsAPI
app = FastAPI()
app.include_router(SettingsAPI.router)

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

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


wsmanager = ConnectionManager()
wsAPI = WebSocketAPI.WebSocketAPI(wsmanager)

#AxisManager = StageControl.Controller.AxisManager(wsmanager)
#StageManager = StageControl.Controller.StageManager(wsmanager, AxisManager)


@app.websocket("/ws/")
async def websocket_endpoint(websocket: WebSocket):
    # Add to WS manager
    await wsmanager.connect(websocket)
    try:
        # Wait for new data
        while True:
            # Try parsing the data and sending it to the wsAPI handler
            data = await websocket.receive_json()
            await wsAPI.receive(data, websocket)
    except WebSocketDisconnect:
        # handle the disconnect through the ws manager.
        wsmanager.disconnect(websocket)
    except Exception as e:
        res = {
            "response": "error",
            "error": str(e)
        }
        await websocket.send_json(res)

