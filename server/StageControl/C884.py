from enum import Enum

from pipython import GCSDevice
from pipython.pitools import pitools
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

class C884Status(Enum):
    disconnected = "disconnected"
    connected = "connected"
    connecting = "connecting"
    error = "error"
    connection_error = "connection_error"
    referencing = "referencing"

class C884:
    """
    Class used to interact with a single PI C-884 controller.
    Remember to close the connection once you are done with the controller to avoid blocking the com port - especially
    during setup.
    """

    def __init__(self, config: C884Config):
        """
        Initialize the controller and reference all axes, communication is over RS232. Throws an exception if it fails.

        A device which is not powered or improperly connected will raise an error!
        """
        # Start up GCS device
        self.device: GCSDevice = GCSDevice("C-884")

        # Set up configs
        self.comport: int = config.comport
        self.baudrate: int = config.baudrate
        self.stages: [str] = config.stages

        # Set up flags
        self.status: C884Status = C884Status.disconnected
        self.error: str = ""

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
            await pitools.startup(self.device, stages=config.stages, refmodes=None)

    def getConfig(self) -> C884Config:
        config = C884Config()
        config.comport = self.comport
        config.baudrate = self.baudrate
        config.stages = self.stages
        return config

    async def startReferencing(self, refmodes=None):
        # References axis, i.e. calibration
        # Create array of refmodes

        # Attempt to reference the given axes
        if refmodes is None:
            refmodes = ["FRF, FRF, FRF, FRF"]
        try:
            await pitools.startup(self.device, refmodes=refmodes)
        except Exception as e:
            # Raise Exception
            raise e

    async def getPos(self) -> dict:
        """
        Gets position(s) of devices connected to the channel(s)
        @return: [1: val, 2: val, etc.]
        """
        try:
            return await self.device.qPOS()  # [1: val, 2: val, etc.]
        except Exception as e:
            raise Exception("Motor Error", "Error getting position: " + str(e))

    async def moveTo(self, channel: int, target):
        """
        Moves channel(s) to target(s)
        @param channel: Integer of channel to which device(s) is/are connected
        @param target: Float of target position(s)
        """

        try:
            await self.device.MOV(channel, target)

        except Exception as e:
            raise Exception("Error Moving Motor: " + str(e))

    async def onTarget(self) -> dict:
        """
        Returns boolean of whether the axis/axes are on target.
        @return: Boolean or array of booleans of whether the axes are on target.
        """

        try:
            return await self.device.qONT()

        except Exception as e:
            raise Exception("Unable to get target status: " + str(e))

    async def openConnection(self):
        """
        Opens connection to controller device if not already connected
        """
        if self.device.IsConnected:
            return
        else:
            # try to connect, set the appropriate status flags
            try:
                self.status = C884Status.connecting
                await self.device.ConnectRS232(self.comport, self.baudrate)
                self.status = C884Status.connected
            except Exception as e:
                self.status = C884Status.connection_error
                self.error = str(e)
                self.closeConnection()

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
