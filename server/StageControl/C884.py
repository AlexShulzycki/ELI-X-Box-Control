from pipython import GCSDevice
from pipython.pitools import pitools


class C884:
    """
    Class used to interact with a single PI C-884 controller.
    Remember to close the connection once you are done with the controller to avoid blocking the com port - especially
    during setup.

    """

    def __init__(self, comport, baudrate, stages):
        """
        Initialize the controller and reference all axes, communication is over RS232. Throws an exception if it fails.
        @param comport: COM port to which the device is connected
        @param baudrate: Baudrate with which to communicate over RS232. Default for the C-884 is 115200.
        @param stages: Array of 4 devices connected on the controller, in order from channel 1 to 4. If no stage is
        present, "NOSTAGE" is required. Example: Channel 1 and 3 are connected: ['L-406.20DD10','NOSTAGE', 'L-611.90AD',
         'NOSTAGE']
        A device which is not powered or improperly connected will raise an error!
        """
        # Run the super for the heck of it, it doesn't do anything anyway
        super().__init__()

        # Dict of axes connected to the controller
        self.axes = {}  # {axis name: Axis}

        # Connect to the device

        self.device: GCSDevice = GCSDevice("C-884")
        self.comport = comport
        self.baudrate = baudrate
        self.stages = stages
        self.device.ConnectRS232(comport, baudrate)

        # Create array of refmodes
        refmode = []
        for i in stages:
            refmode.append("FRF")

        # Attempt to reference the given axes
        try:
            print("Startup and Referencing - this can take a while")
            pitools.startup(self.device, stages=stages, refmodes=refmode)
            print("Finished referencing")
        except Exception as e:
            # close connection and raise exception
            self.closeConnection()
            raise e

        # Everything worked, the controller is configured and valid
        return

    def getPos(self) -> dict:
        """
        Gets position(s) of devices connected to the channel(s)
        @return: {cryy: 25, cryx: 12, etc.}
        """
        response = []
        try:
            # Open connection and grab data on positions
            self.openConnection()
            response = self.device.qPOS(self.getChannels())  # [1: val, 2: val, etc.]
        except Exception as e:
            raise Exception("Motor Error", "Error getting position: " + str(e))

        #  Otherwise, lets create the result dict
        result = {}
        for axis in list(self.axes.values()):
            # Correlate channel with axis
            channel = axis.channel
            # Get the proper pos, i.e. check if its reversed and do necessary calculations
            result[axis.axis] = axis.getProperPos(response[channel])

        return result

    def getPosChannel(self, channel: int) -> float:
        """
        Get position of a device from the given channel
        @param channel: Integer 1 through 4
        @return: Raw position value (i.e. not checked if corresponding axis is reversed) read from the controller
        """
        try:
            # Open connection and grab data on positions
            self.openConnection()
            response = self.device.qPOS(self.getChannels())  # [1: val, 2: val, etc.]
            # If we got a channel passed into the function, only return that response
            return response[channel]
        except Exception as e:
            raise Exception("Error getting position: " + str(e))

    def move(self, channel: int, target):
        """
        Moves channel(s) to target(s)
        @param channel: Integer of channel to which device(s) is/are connected
        @param target: Float of target position(s)
        """

        try:
            self.openConnection()
            self.device.MOV(channel, target)

        except Exception as e:
            raise Exception("Error Moving Motor: " + str(e))

    def onTargetChannel(self, channel: int) -> bool:
        """
        Get onTarget status of a channel
        @param channel: Integer 1 through 4
        @return: Whether the stage connected to the channel is on target
        """
        try:
            # Open connection and get onTarget
            self.openConnection()
            res = self.device.qONT(self.getChannels())

            # If we got a channel passed into the function, only return that
            if channel is not None:
                return res[channel]
        except Exception as e:
            raise Exception("Error getting target: " + str(e))

    def onTarget(self) -> dict:
        """
        Returns boolean of whether the axis/axes are on target.
        @param channel: Integer channel or array of channels. If not give, all axes will be queried
        @return: Boolean or array of booleans of whether the axes are on target.
        """

        try:
            # Open connection and get onTarget
            self.openConnection()
            res = self.device.qONT(self.getChannels())

            # Correlate channels with axes and put into dict
            result = {}
            for axis in list(self.axes.values()):
                # Create format {axis name: true/false}
                result[axis.axis] = res[axis.channel]

            return result

        except Exception as e:
            raise Exception("Unable to get target status: " + str(e))

    def openConnection(self):
        """
        Opens connection to controller device if not already connected
        """
        if self.device.IsConnected:
            return
        else:
            self.device.ConnectRS232(self.comport, self.baudrate)

    def closeConnection(self):
        """
        Closes connection to the controller device
        """
        self.device.CloseConnection()
        print("Disconnected")

    def range(self, channel):
        """
        Returns the [min,max] for the selected channel
        @param channel: A single channel to check the min max on
        @return: [min,max]
        """
        self.openConnection()
        return [self.device.qTMN(channel)[channel], self.device.qTMX(channel)[channel]]

    def getChannels(self):
        """
        Returns list of channels (integers) from the list of axes connected to the controller
        @return: [int]
        """
        channels = []
        for axis in list(self.axes.items()):
            channels.append(axis[1].channel)  # Items() returns tuple, grab the value only
        return channels

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.closeConnection()

    def __eq__(self, other):
        #  So we can compare controllers to see if they are identical
        return self.__dict__ == other.__dict__
