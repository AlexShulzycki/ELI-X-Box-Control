from __future__ import annotations

import glob
import sys
from typing import Any

import serial

from server.Devices import Device, Action, Configuration
from server.Devices.Events import ConfigurationUpdate, updateResponse, Notice, DeviceUpdate
from server.utils.EventAnnouncer import EventAnnouncer


class ControllerInterface:
    """
    Base class of controller interfaces. Make sure you pass on any updates to the event announcer.

    """

    def __init__(self):
        self.EventAnnouncer = EventAnnouncer(ControllerInterface, DeviceUpdate, Notice, ConfigurationUpdate)

    @property
    def devices(self) -> list[Device]:
        """List of devices this controller controls"""
        raise NotImplementedError

    @property
    def deviceIDs(self) -> list[int]:
        """List of device IDs this controller has under its wing"""
        res = []
        for device in self.devices:
            res.append(device.id)
        return res

    async def execute_action(self, identifier, action, value: None|bool|float|str) -> None:
        """Executes an action on a given device.
        :param identifier: Device identifier
        :param action: Action to execute
        :param value: Value of the action
        """
        raise NotImplementedError

    @property
    def device_schemas(self) -> list[dict[str, Any]]:
        """Returns a JSON-ready dict of devices this controller can configure"""
        raise NotImplementedError

    @property
    def configurationIDs(self) -> list[int]:
        """Returns a list of configuration IDs this controller controls"""
        res = []
        for config in self.currentConfigurations:
            res.append(config.ID)
        return res

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
    async def configurationSchema(self) -> dict:
        """
        Return the configuration object json schema
        :return:
        """
        raise NotImplementedError

    @property
    def configurationPydanticModel(self):
        """Returns the pydantic model of a valid configuration"""
        raise NotImplementedError

    @property
    def currentConfigurations(self) -> list[Configuration]:
        """Returns the list of current configurations"""
        raise NotImplementedError

    async def refresh_devices(self, ids:list[int]|None = None) -> None:
        """Refreshes all values for given devices"""
        raise NotImplementedError

    async def refresh_configurations(self, ids: list[int]|None = None) -> None:
        """Refreshes all configurations"""
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

    @property
    def name(self) -> str:
        raise NotImplementedError

# Helper Functions

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
