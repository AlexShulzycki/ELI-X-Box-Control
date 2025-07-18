from enum import Enum

from pydantic import BaseModel, Field, field_validator

from server.StageControl.DataTypes import ControllerSettings, StageStatus, StageInfo


class C884Settings(BaseModel):
    pass

class PIConnectionType(Enum):
    usb = "usb"
    rs232 = "rs232"
    network = "network"

class PIControllerModel(Enum):
    C884 = "C884"
    mock = "mock"

class PIControllerStatus(BaseModel):
    SN: int = Field(description="Serial number of the controller")
    model: PIControllerModel = Field(description="Name of the model", examples=[PIControllerModel.C884])
    connection_type: PIConnectionType = Field(description="How the controller is connected")
    connected: bool = Field(examples=[True, False], description="If the controller is connected")
    channel_amount: int = Field(examples=[0], description="Number of channels controller supports")
    ready: bool = Field(examples=[True, False], description="Whether the controller is ready")
    referenced: list[bool] = Field(examples=[[True, False, False, False]],
                                   description="Whether each axis is referenced")
    clo: list[bool] = Field(examples=[[True, False, True, False]],
                            description="Whether each axis is in closed loop operation, i.e. if its turned on")
    stages: list[str] = Field(default=["NOSTAGE", "NOSTAGE", "NOSTAGE", "NOSTAGE"], min_length=4,
                              examples=[['L-406.20DD10', 'NOSTAGE', 'L-611.90AD', 'NOSTAGE']])
    """Array of 4 devices connected on the controller, in order from channel 1 to 4, or 6. If no stage is
        present, "NOSTAGE" is required. Example: Channel 1 and 3 are connected: ['L-406.20DD10','NOSTAGE', 'L-611.90AD',
         'NOSTAGE']"""
    error: str = Field(description="Error message. If no error, its an empty string")
    baud_rate: int = Field(default=None, description="Baud rate of RS232 connection.")
    comport: int = Field(default = None, description="Comport for RS232 connection.")

    @field_validator("referenced", "clo", "stages")
    def validate_channel_amounts(self, value):
        if self.channel_amount != len(value):
            raise ValueError("Needs to match number of channels")
        return value

    @field_validator("connection_type")
    def validate_required_fields(self, value):
        if value is PIConnectionType.rs232:
            if self.baud_rate is None or self.comport is None:
                raise ValueError("Baud rate and comport must be specified for an RS232 connection")

        return value

class PIStageInfo(StageInfo):
    controllerSN: int  = Field(description="SN of controller controlling this stage")
    channel: int = Field(description="Which controller channel this stage is connected to")


    # the identifier is supposed to be (controller SN)(channel number) so we check this is true
    # I cant be bothered to do the math thing so we check using strings, sorry.
    @field_validator("controllerSN")
    def validate_controllerSN(cls, value):
        if str(cls.identifier)[:-1] != str(value):
            raise ValueError(f"SN {value} doesnt match identifier")
        return value

    @field_validator("channel")
    def validate_controllerSN(cls, value):
        if str(cls.identifier)[-1] != str(value):
            raise ValueError(f"SN {value} doesnt match identifier")
        return value


class PISettings(ControllerSettings):

    def __init__(self):
        ControllerSettings.__init__(self)
        # type hint, this is where we store controller statuses
        self.controllers: dict[int, PIController] = {}


    async def configurationChangeRequest(self, request: PIControllerStatus):
        """
        Tries to turn the desired state into reality.
        :param request: A valid PIController status.
        :return:
        """

        # Try to find a PIControllerStatus with the same serial number
        controller = self.controllers[request.SN]

        #If we haven't found it, we set up a new connection
        if controller is None:
            return self.newController(request)

        # Update the relevant controller
        return self.updateController(request)

    async def removeConfiguration(self, SN: int):
        """
        Removes a controller.
        :param SN: Serial number of the controller.
        :return:
        """
        await self.controllers[SN].shutdown_and_cleanup()
        self.controllers.pop(SN)


    def newController(self, status: PIControllerStatus):
        if status.model == PIControllerModel.mock:
            self.controllers[status.SN] = TestPIController(status)
        if status.model == PIControllerModel.C884:
            # TODO IMPLEMENT A C884
            #self.controllers[status.SN] = C884(status)
            pass

    def updateController(self, status: PIControllerStatus):
        if self.controllers[status.SN] is not None:
            self.controllers[status.SN].updateFromStatus(status)

    def getDataTypes(self) -> list[type]:
        return [PIStageInfo, PIControllerStatus]


    @property
    def stageStatus(self) -> dict[int, StageStatus]:
        """Return stage status of properly configured and ready stages"""
        raise NotImplementedError

    @property
    def stageInfo(self) -> dict[int, PIStageInfo]:
        raise NotImplementedError



class PIController:

    def addFromStatus(self, status: PIControllerStatus):
        raise NotImplementedError

    def updateFromStatus(self, status: PIControllerStatus):
        raise NotImplementedError

    def shutdown_and_cleanup(self):
        raise NotImplementedError

    async def refreshFullStatus(self):
        """
        Refresh the entire status of the controller.
        """
        raise NotImplementedError

    async def refreshPosOnTarget(self):
        """
        Just like refreshFullStatus, but only refreshes position and ontarget status.
        """
        raise NotImplementedError

    async def moveTo(self, channel, position: float):
        raise NotImplementedError

    @property
    def status(self) -> PIControllerStatus:
        """
        Construct and return a status object for this controller, WITHOUT asking the controller.
        """
        raise NotImplementedError

class TestPIController(PIController):

    def __init__(self, status: PIControllerStatus):
        pass