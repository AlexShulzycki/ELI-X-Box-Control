import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.openapi.utils import get_openapi
from starlette.staticfiles import StaticFiles

from .API import DeviceAPI, WebSocketAPI, GeometryAPI, KinematicsAPI, ConfigurationAPI

tags_metadata = [
    {
        "name": "settings",
        "description": "Configuring controllers and their axes.",
        "externalDocs": {
            "description": "List of GCS commands",
            "url": "https://www.le.infn.it/~chiodini/allow_listing/pi/Manuals/PIGCS_2_0_DLL_SM151E210.pdf",
        },
    },
    {
        "name": "control",
        "description": "Control axes, i.e. moving them after they are configured with **settings**",
    },
    {
        "name": "calculation",
        "description": "Calculate geometry, angles, offsets, etc..",
    }
]
app = FastAPI(openapi_tags = tags_metadata)

# settings routers
app.include_router(ConfigurationAPI.router)

# Geometry and stage control routers
app.include_router(GeometryAPI.router)
app.include_router(DeviceAPI.router)
app.include_router(KinematicsAPI.router)

wsmanager = WebSocketAPI.websocketapi

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
            print("Disconnected")
            break
        except Exception as e:
            res = {
                "response": "error",
                "error": str(e)
            }
            await websocket.send_json(res)

app.openapi = custom_openapi

# We have to mount the static files after the websockets, because otherwise it will try to serve websockets and
# throw a runtime error.
app.mount("/", StaticFiles(directory="./static", html=True), name="static")


def serve():
    """Serve the web application."""
    uvicorn.run(app)

if __name__ == "__main__":
    serve()