from pipython import GCSDevice
from pipython.pitools import pitools


class C884:
    """
    Class used to interact with a single PI C-884 controller.
    Remember to close the connection once you are done with the controller to avoid blocking the com port - especially
    during setup.

    """

    def __init__(self, comport, baudrate, stages=None):
        """
        Initialize the controller and reference all axes, communication is over RS232. Throws an exception if it fails.
        @param comport: COM port to which the device is connected
        @param baudrate: Baudrate with which to communicate over RS232. Default for the C-884 is 115200.
        @param stages: Array of 4 devices connected on the controller, in order from channel 1 to 4. If no stage is
        present, "NOSTAGE" is required. Example: Channel 1 and 3 are connected: ['L-406.20DD10','NOSTAGE', 'L-611.90AD',
         'NOSTAGE']
        A device which is not powered or improperly connected will raise an error!
        """

        # Dict of axes connected to the controller
        if stages is None:
            stages = ["NOSTAGE", "NOSTAGE", "NOSTAGE", "NOSTAGE"]

        # Connect to the device

        self.device: GCSDevice = GCSDevice("C-884")
        self.comport = comport
        self.baudrate = baudrate
        self.stages = stages

        return

    async def startReferencing(self):
        # References axis, i.e. calibration
        # Create array of refmodes
        refmode = []
        for i in self.stages:
            refmode.append("FRF")

        # Attempt to reference the given axes
        try:
            await pitools.startup(self.device, stages=self.stages, refmodes=refmode)
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
            await self.device.ConnectRS232(self.comport, self.baudrate)

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
