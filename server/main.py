from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.openapi.utils import get_openapi

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

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="ELI X-Box Control API",
        version="0.5",
        description="API for communicating with the X-box server",
        routes=app.routes,
    )
    # Add WebSocket route to the schema
    openapi_schema["paths"]["/ws/"] = {
        "get": {
            "summary": "WebSocket connection, obviously use ws://",
            "responses": {200: {"description": "WebSocket"}},
            # Find a way to add the websocket schema here
        }
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema

@app.websocket("/ws/")
async def websocket_endpoint(websocket: WebSocket):
    # Add to WS manager
    await wsmanager.connect(websocket)
    # Wait for new data
    while True:
        try:
            # Try parsing the data and sending it to the wsAPI handler
            data: WebSocketAPI.Req = await websocket.receive_json()
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

app.openapi = custom_openapi