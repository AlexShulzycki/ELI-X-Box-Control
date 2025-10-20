from __future__ import annotations

import glob
import sys

import serial

from server.Devices.DataTypes import StageStatus, StageInfo, StageRemoved, Notice, ConfigurationUpdate, \
    Configuration, updateResponse
from server.utils.EventAnnouncer import EventAnnouncer


class ControllerInterface:
    """
    Base class of controller interfaces. Make sure you pass on any updates to the event announcer.

    """

    def __init__(self):
        self.EventAnnouncer = EventAnnouncer(ControllerInterface, StageStatus, StageInfo, StageRemoved, Notice, ConfigurationUpdate)

    @property
    def stages(self) -> list[int]:
        """Returns unique integer identifiers for each stage"""
        raise NotImplementedError

    async def moveTo(self, identifier: int, position: float):
        """Move stage to position"""
        raise NotImplementedError

    async def moveBy(self, identifier: int, step: float):
        """Move stage by offset"""
        raise NotImplementedError

    @property
    def stageInfo(self) -> dict[int, StageInfo]:
        """Returns StageInfo of connected stages"""
        raise NotImplementedError

    async def updateStageInfo(self, identifiers: list[int] = None):
        """Updates StageInfo for the given stages or all if identifier list is empty"""
        raise NotImplementedError

    @property
    def stageStatus(self) -> dict[int, StageStatus]:
        """Return StageStatus objects for the given stages"""
        raise NotImplementedError

    async def updateStageStatus(self, identifiers: list[int] = None):
        """Updates stageStatus for the given stages or all if identifier list is empty."""
        raise NotImplementedError

    @property
    def name(self) -> str:
        raise NotImplementedError

    async def configurationChangeRequest(self, request: list[Configuration]) -> list[updateResponse]:
        """
        Upon receiving a configuration object, tries to turn it into reality.
        :param request: configuration status object, same as from currentConfiguration
        :return: Either none, or raise an error
        """
        raise NotImplementedError

    async def removeConfiguration(self, id: int):
        """
        Remove a configuration. This can mean a controller, stage, whatever
        :param id: some kind of id to differentiate it, doesn't need to be a stage identifier.
        :return:
        """
        raise NotImplementedError

    @property
    def configurationType(self) -> type[Configuration]:
        raise NotImplementedError

    @property
    async def configurationSchema(self) -> dict:
        """
        Return the configuration object json schema
        :return:
        """
        raise NotImplementedError

    @property
    def currentConfiguration(self) -> list[Configuration]:
        raise NotImplementedError

    async def fullRefreshAllSettings(self):
        raise NotImplementedError

    async def is_configuration_configured(self, identifiers: list[int]) -> list[int]:
        """
         If the configuration change function does something that has to be checked again,
          i.e. if the stages have not yet finished referencing, then it is refreshed in this function,
          then if the action is completed, i.e. stages finished referencing, we return true. Otherwise,
          we return false and the server will query this function again after a short delay. Any ConfingurationUpdate
          events need to be sent here to update the UI. This function purely exists to allow the server to
          query this function when the need exists.
        :return: List of identifiers we need to check again
        """
        # return [] by default, override this in the individual interface implementations.
        return []


def getComPorts() -> list[int]:
    """
    Lists serial port names. Stolen from https://stackoverflow.com/a/14224477
    :raises EnvironmentError:
        On unsupported or unknown platforms
    :returns:
        A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(int(port[3:]))  # only return the com port number
        except (OSError, serial.SerialException):
            pass
    return result
