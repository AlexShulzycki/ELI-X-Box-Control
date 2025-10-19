# Hardware Interfaces

> All file paths in this chapter will be relative to the **server** folder for brevity.

## Main Interface
In order for the server to communicate with hardware, all relevant information and objects are stored in 
the so-called *main interface*. This resides in **Interface.py** 

The main interface is responsible for storing all objects the server needs to communicate with physical devices.

When a query comes in from the API asking about a specific device, or requests a configuration change, this main
interface will hand off the request to the relevant sub-interface. These sub-interfaces are subclasses of
the [**ControllerInterface**](#controllerinterface) class, defined in **StageControl/DataTypes.py**


## ControllerInterface
Each subclass of ControllerInterface represents a different type/brand of device, and handles it's specific
software and hardware communication needs. Subclasses include:

- [**PIControllerInterface**](PI-Interface.md) for communicating with PI devices such as the C884
- [**StandaInterface**](Standa-Interface.md) for communicating with Standa devices, such as the SMC5
- **VirtualControllerInterface** for debugging and testing

### Functionality
The function a ControllerInterface is that it stores its state as a set of *configurations*. A single *configuration*
can represent an entire controller, as is the case with the [C884 from PI](PI-Interface.md), or a single axis, as is the
case with [Standa's SMC5](Standa-Interface.md).

The controller interface provides a JSON Schema of its specific *configuration*. By giving the controller a schema-compliant 
*configuration*, it will attempt to change its state to reflect that configuration.

When the state of the controller changes, for example when a stage moves, or finishes referencing, the controller will 
announce that fact using its instance of the [Event Announcer](EventAnnouncer.md). This event is then received by the 
[WebSockets handler](Server.md#websockets) and broadcast via WebSockets.

To query or change the controller's *configuration* state, you can use the REST API, and to listen to 
events and receive updates as fast as they occur, simply watch the WebSocket connection.