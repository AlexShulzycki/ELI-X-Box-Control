import asyncio

from pipython import GCSDevice
from pydantic import Field, BaseModel


class C884Config(BaseModel):
    comport: int = Field(examples=[20, 4, 21])
    """Comport to connect to"""
    baudrate: int = Field(default = 115200, examples=[115200])
    """Baudrate, default is 115200"""
    stages: list[str] = Field(default = ["NOSTAGE", "NOSTAGE", "NOSTAGE", "NOSTAGE"], min_length=4, max_length=4,
                          examples=[['L-406.20DD10', 'NOSTAGE', 'L-611.90AD', 'NOSTAGE']])
    """Array of 4 devices connected on the controller, in order from channel 1 to 4. If no stage is
        present, "NOSTAGE" is required. Example: Channel 1 and 3 are connected: ['L-406.20DD10','NOSTAGE', 'L-611.90AD',
         'NOSTAGE']"""

class ControllerNotReadyException(Exception):
    def __init__(self, message = ""):
        self.message = f"Controller not ready! {message}"
        super().__init__(self.message)


class C884:
    """
    Class used to interact with a single PI C-884 controller.
    Remember to close the connection once you are done with the controller to avoid blocking the com port - especially
    during setup.

    AXIS SETUP PROCESS:
    1 Connect the controller, run openConnection(), make sure its plugged in and you have the right com port etc etc
    2 Tell the controller what stages are connected with CST
    2 Check if the axes are turned on with qSVO, otherwise turn on with SVO
    3 Check if axes are referenced with qFRF()
    4 Reference axis with FRF(), this thing will move so be careful
    5 Set soft limits??? working on that. You an also check if the type of axis has to be FRF'd by asking qRON()
    """

    @staticmethod
    def dict2list(fromController: dict) -> list[any] | list[None]:
        """
        Helper function.
        Converts dict received from the controller into a list, putting a None where no stage is connected
        """
        res = [None, None, None, None]
        # The returned dict will not contain keys of stages which are not connected
        for i in range(1, 5):
            try:
                res[i] = fromController[f"{i}"]
            except KeyError:
                # not present, thus not connected, i.e. it's a NOSTAGE
                continue

        return res

    def __init__(self, config: C884Config):
        """
        Initialize the controller and reference all axes, communication is over RS232. Throws an exception if it fails.

        A device which is not powered or improperly connected will raise an error!
        """
        # Start up GCS device
        self.device: GCSDevice.gcsdevice = GCSDevice("C-884").gcsdevice

        # Set up configs
        self.comport: int = config.comport
        self.baudrate: int = config.baudrate
        self.stages: [str] = config.stages

        return

    async def updateConfig(self, config: C884Config):
        if config.comport != self.comport:
            raise Exception(f"Comport {config.comport} differes from current one {self.comport}")

        if config.baudrate != self.baudrate:
            self.closeConnection()
            self.baudrate = config.baudrate
            await self.openConnection()

        if not config.stages == self.stages:
            self.stages = config.stages
            await self.loadStagesToC884()

    async def loadStagesFromC884(self):
        """
        Loads stages configured per axis on controller. Stores these in self.stages.
        :return: self.stages, freshly updated
        """
        self.checkReady()

        res =  self.device.qCST()

        self.stages = self.dict2list(res)

        return self.stages

    async def loadStagesToC884(self):
        """
        Loads stages per axis onto the controller, from self.stages
        :return:
        """
        self.checkReady()
        try:
            self.device.CST({
                1: self.stages[0],
                2: self.stages[1],
                3: self.stages[2],
                4: self.stages[3]
            })
        except Exception as e:
            print(e)
            raise e

    def getConfig(self) -> C884Config:
        config = C884Config(comport = self.comport, baudrate = self.baudrate, stages = self.stages)
        return config


    @property
    def error(self)-> str | None:
        """
        Gets the error from controller
        :return: the error read from the controller
        """
        if self.ready:
            return self.device.GetError()
        else:
            return None

    @property
    def isavailable(self):
        return self.device.isavailable

    @property
    def isconnected(self):
        return self.device.IsConnected()

    @property
    def ready(self):
        return self.isavailable # for now just isavailables

    def checkReady(self, message: str = ""):
        """ Raises ControllerNotReady exception if controlelr is not ready"""
        if not self.ready:
            raise ControllerNotReadyException(message)

    @property
    async def mustBeReferencedFirst(self) -> list[bool| None]:
        """
        Returns true for axes which need to be referenced
        :return:
        """
        self.checkReady()
        return self.dict2list(self.device.qRON(self.device.axes))

    @property
    async def isReferenced(self):
        """
        Returns true for axes already referenced
        :return:
        """
        self.checkReady()
        return self.dict2list(self.device.qFRF(self.device.axes))

    @property
    async def servoCLO(self)-> list[bool| None]:
        """
        Checks if servo is in closed loop operation, i.e. turned on
        :return:
        """
        self.checkReady()
        return self.dict2list(self.device.qSVO(self.device.axes))


    async def setServoCLOTrue(self, axes: list[int] = None):
        """
        Try to set all axes to closed loop operation, i.e. enabling them. if no list is given, all configured axes will
        have their CLO set to true
        :param axes:
        :return:
        """
        if axes is None:
            axes = self.device.axes
        self.device.SVO(axes, [True] * len(axes))

    async def reference(self, axes: list[int] = None):
        """
        Reference the given axes. If none, reference all axes.
        :param axes: for example [1, 2, 4] for servos on channel 1, 2, and 4
        :return:
        """
        self.checkReady()
        if axes is None:
            axes = self.device.axes
        self.device.SVO(axes)

    @property
    async def position(self)-> list[float] | list[None]:
        """
        Gets position of stages from controller
        :return:
        """
        self.checkReady("Cannot get position.")
        return self.dict2list(await self.device.qPOS())

    @position.setter
    async def position(self, pos: list[float]|list[None]):
        self.checkReady("Cannot move axes.")

        awaiters = []
        for index, p in enumerate(pos):
            awaiters.append(self.device.MOV(index+1, p))
        await asyncio.gather(*awaiters)

    async def moveChannelTo(self, channel: int, target):
        """
        Moves channel(s) to target(s)
        @param channel: Integer of channel to which device(s) is/are connected
        @param target: Float of target position(s)
        """
        self.checkReady("Cannot move axis.")

        await self.device.MOV(str(channel), target)

    @property
    async def onTarget(self) -> list[bool] | list[None]:
        """
        Returns boolean of whether the axis/axes are on target.
        @return: Boolean or array of booleans of whether the axes are on target.
        """
        self.checkReady()
        return self.dict2list(await self.device.qONT())

    async def openConnection(self) -> bool:
        """
        Opens connection to controller device if not already connected
        :return: true if successful, false otherwise
        """
        if self.device.connected:
            return True
        else:
            # try to connect, set the appropriate status flags
            try:
                await self.device.ConnectRS232(self.comport, self.baudrate)
                return True
            except Exception as e:
                print(e)
                self.closeConnection()
                return False

    def closeConnection(self):
        """
        Closes connection to the controller device
        """
        self.device.CloseConnection()

    async def range(self, channel):
        """
        Returns the [min,max] for the selected channel
        @param channel: A single channel to check the min max on
        @return: [min,max]
        """
        return [await self.device.qTMN(channel)[channel], await self.device.qTMX(channel)[channel]]

    def __exit__(self):
        self.closeConnection()

    def __eq__(self, other):
        #  So we can compare controllers to see if they are identical
        return self.__dict__ == other.__dict__
