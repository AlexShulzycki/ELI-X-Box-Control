from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import WebSocketAPI
import SettingsAPI
import Interface

app = FastAPI()
app.include_router(SettingsAPI.router)

@app.get("/")
async def root():
    """
    Serves UI
    :return: The UI
    """
    return {"message": "Hello"}

wsmanager = WebSocketAPI.WebSocketAPI()

@app.websocket("/ws/")
async def websocket_endpoint(websocket: WebSocket):
    # Add to WS manager
    await wsmanager.connect(websocket)
    # Wait for new data
    while True:
        try:
            # Try parsing the data and sending it to the wsAPI handler
            data = await websocket.receive_json()
            await wsmanager.receive(data, websocket)
        except WebSocketDisconnect:
            # handle the disconnect through the ws manager.
            wsmanager.disconnect(websocket)
        except Exception as e:
            res = {
                "response": "error",
                "error": str(e)
            }
            await websocket.send_json(res)

