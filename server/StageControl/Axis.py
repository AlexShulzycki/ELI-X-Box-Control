from C884 import C884
from libximc.highlevel import Axis as ximcAxis


class Axis:
    def __init__(self, axis: str, reversed=False):
        """
        Creates an Axis object, which interfaces with the physical stage
        @param axis: Name of the axis, i.e. cryy
        @param reversed: Whether the axis is reversed
        """
        self.axis = axis
        self.reversed = reversed
        self.minmax = None

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Stop the motor, close the device
        raise NotImplementedError("Implement exit behavior for " + str(type(self)) + " please!")

    def getProperPos(self, position: float) -> float:
        # Check if in range
        if self.reversed:
            position = self.range()[1] - position

        """
        DOES NOT WORK, CLAIMS 0.0>=0 is FALSE FOR SOME REASON
        if (self.range()[0] >= position) or (self.range()[1] <= position):
            raise Exception("Position " + str(position) + " out of range for " + self.axis + ". The range is"
                            + str(self.range()))
        """

        return position

    def move(self, target: float):
        """
        Move axis to target position
        @param target: Position to move to
        """
        raise NotImplementedError("You need to implement the move method")

    def getPos(self) -> float:
        """
        Gets the position of the axis
        @return: Position
        """
        raise NotImplementedError("You need to implement the getPos method")

    def onTarget(self) -> bool:
        """
        Checks if is on target (i.e. finished moving)
        @return: True or False, depending if it's on target
        @rtype: bool
        """
        raise NotImplementedError("You need to implement the onTarget method")

    def range(self) -> list:
        """
        Returns the [min,max] range of travel for this axis - must be calculated in the constructor
        """
        raise NotImplementedError("You need to implement the range method. Do not interact with minmax directly")


class PIAxis(Axis):
    """
    Class that represents a single connected motor/stage to the controller. Methods are passed through to the drumController
    class.
    """

    def __init__(self, axis: str, controller: C884, channel: int, reversed=False):
        """
        Constructor to store information
        @param controller: drumController that this axis is connected to (drumController class)
        @param channel: Which channel on the controller this axis is connected to (Integer 1-4)
        @param axis: The name of the axis this object represents, i.e. samx
        @param reversed: Uses the axis in reverse mode
        """
        # define the axis
        super().__init__(axis, reversed)
        self.controller: C884 = controller
        self.channel = channel

        # Add this axis to the controller axes dict
        self.controller.axes[self.axis] = self

        # Check if we can use reversed mode - i.e. if the motor has limit switches
        if reversed and self.isReversable():
            self.reversed = True
        pass

    def move(self, target: float):
        """
        Move axis to target position.
        @param target: Position to move to
        """
        target = self.getProperPos(target)
        self.controller.move(self.channel, target)

    def getPos(self) -> float:
        """
        Gets the position of the axis at this point in time
        @return: Position of the axis, already adjusted if it is reversed
        """
        return self.getProperPos(self.controller.getPosChannel(self.channel))

    def onTarget(self) -> bool:
        return bool(self.controller.onTargetChannel(self.channel))

    def range(self) -> list:
        """
        Returns the [min,max] range of travel for this axis - only calculates once, then stores it in the object.
        """
        # Check if min max has already been calculated, if not then calculate it
        if self.minmax is None:
            self.minmax = self.controller.range(self.channel)

        return self.minmax

    def isReversable(self) -> bool:
        """
        Check if this axis is reversable, i.e. if it has limit switches
        @return:
        """
        # TODO low priority, we do not have stage where this is necessary yet
        return True


class StandaAxis(Axis):
    def __init__(self, axis: str, uri: str, calibration: float, minmax, reversed=False):
        """
        Initializes a Standa device axis
        @param axis: Name of the axis, i.e. cryy
        @param uri: URI of the axis
        @param calibration: mm per step
        @param minmax: Minimum and maximum travel range of axis
        @param reversed: Whether the axis is in reverse mode
        """
        super().__init__(axis, reversed)
        self.minmax = minmax

        # Open connection
        self.ximc = ximcAxis(uri)
        self.ximc.open_device()

        # Calibrate so positions are in millimeters
        self.ximc.set_calb(calibration, self.ximc.get_engine_settings().MicrostepMode)

    def move(self, target):
        """
        Move axis to target position.
        @param target: Position to move to
        """
        properTarget = self.getProperPos(target)
        self.ximc.command_move_calb(properTarget)

    def getPos(self) -> float:
        """
        Gets the position of the axis
        @return: Position
        """
        return self.getProperPos(self.ximc.get_position_calb().Position)

    def onTarget(self) -> bool:
        """
        Checks if is on target
        @return: True, false
        """
        # Check if the move command status contains the running flag
        return not str(self.ximc.get_status().MvCmdSts).__contains__("MVCMD_RUNNING")

    def range(self) -> list:
        """
        Returns the [min,max] range of travel for this axis
        """
        return self.minmax

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Stop the motor, close the device
        self.ximc.command_stop()
        self.ximc.close_device()


class RotationAxis(Axis):
    def __init__(self, axis: Axis, limit=None):
        """
        RotationAxis object for handling rotating stages
        @param axis: Axis object which handles this stage
        @param limit: The maximum travel range, i.e. if you say you want to move to 190 degrees and the limit is 180,
                    the stage will move to 10 degrees. If None, there is no limit, and you can spin around to your
                    heart's content
        """
        super().__init__(axis.axis, axis.reversed)
        self.axisObject = axis

        # Limit must be greater or equal to 180, TODO make it work with smaller angles
        if limit is None:
            self.limit = None
        elif limit < 180:
            limit = 180
            self.limit = limit
        else:
            self.limit = limit

    def move(self, target: float):
        """
        Move axis to target position.
        @param target: Position to move to
        """
        self.axisObject.move(self.correctAngle(target))

    def getPos(self) -> float:
        """
        Gets the position of the axis
        @return: Position
        """
        return self.axisObject.getPos()

    def onTarget(self) -> bool:
        """
        Checks if is on target (i.e. finished moving)
        @return: True or False, depending if it's on target
        @rtype: bool
        """
        return self.axisObject.onTarget()

    def range(self) -> list:
        """
        Returns the [min,max] range of travel for this axis - in this case we just put the lower and upper limit
        """
        return [-self.limit, self.limit]

    def correctAngle(self, theta: float):
        """
        Corrects the angle to be within -185 to 185 degrees.
        @param theta: Angle in degrees
        @return: The corrected angle
        """
        # If we have no limit, just return theta
        if self.limit is None:
            return theta

        # Correct the angle (if we need to)
        if theta > self.limit:
            while theta > self.limit:
                theta -= 360
        elif theta < -self.limit:
            while theta < -self.limit:
                theta += 360

        # Angle is either already within limits, or has been corrected to be within limits
        return theta


class PIRotationAxis(RotationAxis):

    def __init__(self, axis: PIAxis, limit=185):
        """
        RotationAxis object for handling PI rotation stages.
        @param axis: PIAxis object which handles this stage
        @param limit: Max travel range in either direction, default is 185 degrees.
        """
        # Call the super class
        super().__init__(axis, limit)
        self.axisObject: PIAxis  # For the IDE to know we are dealing with a PIAxis

        # Set acceleration
        acceleration = 20
        self.axisObject.controller.device.gcscommands.ACC(self.axisObject.channel, acceleration)
        self.axisObject.controller.device.gcscommands.DEC(self.axisObject.channel, acceleration)



    # dunno if this works or is necessary to avoid angle being referenced changing between startups and or tangling the
    # wires up by rotating 360 degrees - todo this will only work if we delete all axes on program exit
    # def __del__(self):
    #    self.angle.move(5)  # Referencing always happens from one direction, move the stage before referencing
