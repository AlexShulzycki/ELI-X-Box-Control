# COPYPASTED FROM THE PREVIOUS SOFTWARE, THUS NON-FUNCTIONAL:  USE THIS AS A GUIDE ONLY
from server.Interface import toplevelinterface as interface
from server.StageControl.DataTypes import StageInfo, StageStatus, StageKind


class Axis:
    def __init__(self, identifier: int, reversed = False):
        """
        Creates an Axis object, which interfaces with the physical stage
        @param identifier: Unique identifier for the stage this axis controls
        @param reversed: Whether the axis is reversed
        """
        # Set up identifier, this fails if there is no stage with the give identifier
        self._identifier = None
        self.identifier = identifier

        self.reversed = reversed
        self.minmax = None

        # create a blank stagestatus and stageinfo
        self.status = StageStatus(identifier = identifier)
        self.info = StageInfo(
            model = "N/A",
            identifier = self.identifier,
        )

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Stop the motor, close the device
        raise NotImplementedError("Implement exit behavior for " + str(type(self)) + " please!")

    @property
    def identifier(self) -> int:
        return self._identifier

    @identifier.setter
    def identifier(self, value:int):
        """Sets the identifier for the axis. Exception if this identifier is not present in any interface"""
        if interface.getRelevantInterface(value) is not None:
            # Identifier exists, we can use it
            self._identifier = value
        else:
            # Does not exist in any control interface, we cannot use it.
            raise Exception(f"Stage identifier {value} is not present in any interface")

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

    async def move(self, target: float):
        """
        Move axis to target position
        @param target: Position to move to
        """
        interface.getRelevantInterface(self.identifier).moveTo(target)

    async def getUpdatedStatus(self)-> StageStatus:
        self.status = interface.getRelevantInterface(self.identifier).stageInfo([self.identifier])[0]
        return self.status

    def getStatus(self) -> StageStatus:
        """
        Gets the StageStatus that was last known. Does not query the axis for an update.
        :return: Last known StageStatus, not necessarily up to date!
        """
        return self.status

    async def getUpdatedStageInfo(self) -> StageInfo:
        self.info = await interface.getRelevantInterface(self.identifier).stageInfo([self.identifier])[0]
        return self.info

    def getStageInfo(self) -> StageInfo:
        """
        Gets the StageInfo that was last known. Does not query the axis for an update.
        :return: Last known StageInfo, not necessarily up to date!
        """
        return self.info

    async def getPos(self) -> float:
        """
        Gets the position of the axis
        @return: Position
        """
        status = await self.getStatus()
        return status.position

    async def onTarget(self) -> bool:
        """
        Checks if is on target (i.e. finished moving)
        @return: True or False, depending if it's on target
        @rtype: bool
        """
        status = await self.getStatus()
        return status.ontarget

    async def range(self) -> list:
        """
        Returns the [min,max] range of travel for this axis - must be calculated in the constructor
        """
        info: StageInfo = await interface.getRelevantInterface(self.identifier).stageInfo([self.identifier])[0]
        return [info.minimum, info.maximum]


### EVERYTHING BELOW IS NON-FUNCTIONAL AND FOR REFERENCE ONLY ###
###
###
###


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

