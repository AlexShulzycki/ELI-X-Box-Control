# Server API

The server is in essence a REST API powered by FastAPI which calls relevant code. It lives in the  **server** folder.

> All file paths in this chapter will be relative to the **server** folder for brevity.

## main.py
This is the file that ties everything together. It starts the FastAPI server, and passes it additional APIs defined 
in the **API** folder.

### REST API
This consists of GET and POST requests, and are defined in the **API** subfolder.

These include:
- **ConfigurationAPI.py**
- **StageControlAPI.py**
- **GeometryAPI.py**

### Websockets
For pushing data to the web interface (or any other software), we implement a websocket client.
The websocket client is mounted in **main.py**, and the implementation resides in **API/WebSocketAPI.py** 



## API Reference
>The API reference is available from the browser at  `rooturl/docs`.
> The root url is usually localhost:8000 when running FastAPI from the IDE.
{style="note"}

The API reference is generated automatically and dynamically by FastAPI, so any and all 
documentation and schemas are passed to and processed by FastAPI. 

This ensures strict API definitions, and the documentation basically writes itself while coding.