from __future__ import annotations

import importlib
import pkgutil

import asyncio
from typing import Any

import Devices

from server.Devices import Configuration, Action
from server.Devices.Events import DeviceUpdate, ConfigurationUpdate, Notice, updateResponse, ActionRequest
from server.Devices.Interface import ControllerInterface
from server.Devices.PI.C884 import ControllerNotReadyException
from server.utils.EventAnnouncer import EventAnnouncer

class DeviceInterface:
    """This interface communicates with device interfaces and holds information on
    configurations and specific devices"""

    def __init__(self, *dev_intfs: ControllerInterface):

        self._device_interfaces: dict[str, ControllerInterface] = {}
        self.EventAnnouncer: EventAnnouncer = EventAnnouncer(DeviceInterface, DeviceUpdate, ConfigurationUpdate, Notice)
        for intf in dev_intfs:
            self.addInterface(intf)

    @property
    def device_interfaces(self) -> dict[str, ControllerInterface]:
        return self._device_interfaces

    def addInterface(self, intf: ControllerInterface):
        """
        Adds a ControllerInterface to this interface. Checks if already added, also sets up the
        event announcer.
        :param intf: controller interface to add.
        :return:
        """
        if self._device_interfaces.__contains__(intf.name):
            # Already exists here
            raise Exception(f"Couldn't add interface {intf} to main device interface, as its already been added")

        # New interface, lets sub to their event announcer and feed it directly into ours
        self.EventAnnouncer.patch_through_from(self.EventAnnouncer.availableDataTypes, intf.EventAnnouncer)

        # All done, finally append to the list
        self._device_interfaces[intf.name] = intf

        print(f"{intf.name} device interface is online")

    @property
    async def configuration_schema(self) -> dict[str, Any]:
        """Returns list of JSON schemas of valid configuration types"""
        res = {}
        for intf in self.device_interfaces.values():
            res[intf.name] = await intf.configurationSchema
        return res

    async def updateConfigurations(self, configs: list[Configuration]) -> list[updateResponse]:
        """Send the configurations to their relevant device interfaces, returns their responses"""
        awaiters = []
        for config in configs:
            if self.device_interfaces.__contains__(config.ControllerType):
                awaiters.append(self.device_interfaces[config.ControllerType].configurationChangeRequest([config]))
            else:
                awaiters.append(await updateResponse(identifier=config.ID, success=False,
                                                     error=f"Controller interface for {config.ControllerType} not found"))

        return await asyncio.gather(*awaiters)

    async def refreshConfigurations(self, configIDs: list[int] | None = None):
        """Tells each controller interface to refresh the given configurations"""
        awaiters = []
        for intf in self.device_interfaces.values():
            awaiters.append(intf.refresh_configurations(configIDs))

        await asyncio.gather(*awaiters)

    async def refreshDevices(self, deviceIDs: list[int] | None = None):
        """Tells each controller interface to refresh the given devices"""
        awaiters = []
        for device_id in deviceIDs:
            awaiters.append(self.getDeviceController(device_id).refresh_devices(deviceIDs))

        await asyncio.gather(*awaiters)

    def getDeviceController(self, deviceID: int) -> ControllerInterface:
        """Returns the controller for the given device ID"""
        for intf in self.device_interfaces.values():
            if deviceID in intf.deviceIDs:
                return intf

        # we didn't find the device!
        raise Exception(f"Device {deviceID} not found")

    async def execute_actions(self, actions: list[ActionRequest]) -> None:
        """Executes given actions"""
        awaiters = []
        for action in actions:
            awaiters.append(self.getDeviceController(action.device_id).execute_action(action))

        await asyncio.gather(*awaiters)



# automatically import interfaces from each subpackage
deviceInterfaces: list[ControllerInterface] = []
for importer, modname, ispkg in pkgutil.iter_modules(Devices.__path__):
    if ispkg:
        module = importlib.import_module(f"Devices.{modname}")
        if hasattr(module, "controller_interface"):
            deviceInterfaces.append(module.controller_interface)
            print(f"Device Controller {module} imported")

# create the top level interface
toplevelinterface = DeviceInterface(*deviceInterfaces)
