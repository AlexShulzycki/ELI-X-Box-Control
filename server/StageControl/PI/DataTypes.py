from enum import Enum

import time
from xml.sax.handler import property_dom_node

from pydantic import BaseModel, Field, field_validator
from pydantic_core.core_schema import FieldValidationInfo

from server.StageControl.DataTypes import ControllerSettings, StageStatus, StageInfo, EventAnnouncer, StageKind
from server.StageControl.PI.C884 import C884


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
    connected: bool = Field(default= False, examples=[True, False], description="If the controller is connected")
    channel_amount: int = Field(default= [], examples=[0], description="Number of channels controller supports")
    ready: bool = Field(default= [], examples=[True, False], description="Whether the controller is ready")
    referenced: list[bool|None] = Field(default=[], examples=[[True, False, False, False]],
                                   description="Whether each axis is referenced")
    clo: list[bool|None] = Field(default=[], examples=[[True, False, True, False]],
                            description="Whether each axis is in closed loop operation, i.e. if its turned on")
    stages: list[str] = Field(default=[],
                              examples=[['L-406.20DD10', 'NOSTAGE', 'L-611.90AD', 'NOSTAGE']])
    """Array of 4 devices connected on the controller, in order from channel 1 to 4, or 6. If no stage is
        present, "NOSTAGE" is required. Example: Channel 1 and 3 are connected: ['L-406.20DD10','NOSTAGE', 'L-611.90AD',
         'NOSTAGE']"""
    error: str = Field(description="Error message. If no error, its an empty string", default="")
    baud_rate: int = Field(description="Baud rate of RS232 connection.", default=115200, examples=[115200])
    comport: int = Field(default = None, description="Comport for RS232 connection.")

    @field_validator("referenced", "clo", "stages", mode="after")
    def validate_channel_amounts(cls, value, info: FieldValidationInfo):
        if info.data["channel_amount"] != len(value):
            raise ValueError("Needs to match number of channels")
        return value

    @field_validator("connection_type", mode="after")
    def validate_required_fields(cls, value, info: FieldValidationInfo):
        if value is PIConnectionType.rs232:
            if info.data["baud_rate"] is None or info.data['comport'] is None:
                raise ValueError("Baud rate and comport must be specified for an RS232 connection")

        return value
    @field_validator("ready")
    def not_ready_if_disconnected(cls, value, info: FieldValidationInfo):
        if not info.data["connected"]:
            return False
        else: return value

    # If disconnected put all relevant fields into a "clean" slate
    @field_validator( "referenced", "clo")
    def disconnected_ref_clo(cls, value, info: FieldValidationInfo):
        """Controller can't be in CLO or referenced if disconnected."""
        if not info.data["connected"]:
            return info.data["channel_amount"] * [False]
        else: return value
    @field_validator( "stages")
    def disconnected_stages(cls, value, info: FieldValidationInfo):
        if not info.data["connected"]:
            return info.data["channel_amount"] * ["NOSTAGE"]
        else: return value

    @field_validator( "ready")
    def disconnected_not_ready(cls, value, info: FieldValidationInfo):
        if not info.data["connected"]:
            return False
        else: return value

class PIStageInfo(StageInfo):
    controllerSN: int  = Field(description="SN of controller controlling this stage")
    channel: int = Field(description="Which controller channel this stage is connected to")

    # the identifier is supposed to be (controller SN)(channel number) so we check this is true
    # I cant be bothered to do the math thing so we check using strings, sorry.
    @field_validator("controllerSN", mode="after")
    def validate_controllerSN(cls, value, info: FieldValidationInfo):
        if str(info.data["identifier"])[:-1] != str(value):
            raise ValueError(f"SN {value} doesnt match identifier")
        return value

    @field_validator("channel")
    def validate_controllerSN(cls, value, info: FieldValidationInfo):
        if str(info.data["identifier"])[-1] != str(value):
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
            self.controllers[status.SN] = MockPIController(status)
        if status.model == PIControllerModel.C884:
            self.controllers[status.SN] = C884(status)
            pass

    def updateController(self, status: PIControllerStatus):
        if self.controllers[status.SN] is not None:
            self.controllers[status.SN].updateFromStatus(status)

    def getDataTypes(self) -> list[type]:
        return [PIStageInfo, PIControllerStatus]


    @property
    def stageStatus(self) -> dict[int, StageStatus]:
        """Return stage status of properly configured and ready stages"""
        res = []
        for cntrl in self.controllers.values():
            res.extend(cntrl.stageStatuses)

    @property
    def stageInfo(self) -> dict[int, PIStageInfo]:
        res = []
        for cntrl in self.controllers.values():
            res.extend(cntrl.stageInfos)



class PIController:

    def __init__(self, status: PIControllerStatus):
        self.EA = EventAnnouncer(StageStatus, StageInfo)

        # Initialize up an empty status
        self._status: PIControllerStatus = PIControllerStatus(
            SN=status.SN,
            model=status.model,
            connection_type=status.connection_type
        )

        # Set up the controller with user config
        self.updateFromStatus(status)

    async def updateFromStatus(self, status: PIControllerStatus):
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

    @property
    def stageInfos(self) -> list[PIStageInfo]:
        raise NotImplementedError

    @property
    def stageStatuses(self) -> list[StageStatus]:
        raise NotImplementedError

class MockPIController(PIController):
    """
    PI controller that's not real, used for testing, doesn't connect to anything, but acts like one.
    """
    def __init__(self, status: PIControllerStatus):
        self._status: PIControllerStatus = None
        self.position: list[float] = [0] * status.channel_amount
        super().__init__(status)


    async def connect(self):
        time.sleep(0.1)
        self._status.connected = True

    async def reference(self, toreference):
        time.sleep(0.1)
        self._status.referenced = toreference

    async def load_stages(self, stages):
        time.sleep(0.1)
        self._status.stages = stages

    async def enable_clo(self, clo):
        time.sleep(0.1)
        self._status.clo = clo

    async def updateFromStatus(self, status: PIControllerStatus):
        # Go through each parameter step by step
        if not self.status.connected and status.connected:
            #connect
            await self.connect()

        if status.stages != self.status.stages:
            await self.load_stages(status.stages)

        if status.clo != self.status.clo:
            await self.enable_clo(status.clo)

        if status.referenced != self.status.referenced:
            await self.reference(status.referenced)

        # TODO find a way to simulate this more closely
        self._status.ready = True

    def shutdown_and_cleanup(self):
        pass

    async def refreshFullStatus(self):
        pass

    async def refreshPosOnTarget(self):
        pass

    async def moveTo(self, channel:int, position: float):
        self.position[channel + 1] = position

    @property
    def status(self) -> PIControllerStatus:
        return self._status

    @property
    def stageStatuses(self) -> list[StageStatus]:
        res = []
        for i in range(self.status.channel_amount):
            res.append(StageStatus(
                position=self.position[i],
                ontarget=True,
            ))

        return res

    @property
    def stageInfos(self) -> list[PIStageInfo]:

        res = []
        for i in range(self.status.channel_amount):
            res.append(PIStageInfo(
                model = "mock stage",
                identifier = self.status.SN * 10 + (i+1),
                kind = StageKind.linear,
                minimum = 0,
                maximum = 10,
                channel = i+1,
                controllerSN = self.status.SN
            ))

        return res