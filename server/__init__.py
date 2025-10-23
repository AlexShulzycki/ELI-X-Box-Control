from __future__ import annotations
import asyncio
from typing import Any

from server.Devices import Configuration, Action, Virtual, PI
from server.Devices.Events import DeviceUpdate, ConfigurationUpdate, Notice, updateResponse, ActionRequest
from server.Devices.Interface import ControllerInterface
from server.Devices.PI.C884 import ControllerNotReadyException
from server.utils.EventAnnouncer import EventAnnouncer


# Device controller packages we want to use with the server.
# I tried to make this automatic, but amount of things that can be broken and the debugging needed
# for it far outweighs the benefit of saving the 2.4 milliseconds to type it in manually in the array below.
device_packages = [Virtual, PI]


class DeviceInterfaceInterface:
    """This interface communicates with device interfaces and holds information on
    configurations and specific devices.
    Thus, it is an interface for device interfaces, i.e. a device interface interface."""

    def __init__(self, *dev_intfs: ControllerInterface):

        self._device_interfaces: dict[str, ControllerInterface] = {}
        self.EventAnnouncer: EventAnnouncer = EventAnnouncer(DeviceInterfaceInterface, DeviceUpdate, ConfigurationUpdate, Notice)
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

        return awaiters

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




# Verify the device packages have an interface in their __init__.py and add them to the main device interface
device_interfaces: list[ControllerInterface] = []
for devpkg in device_packages:
    if hasattr(devpkg, "controller_interface"):
        device_interfaces.append(devpkg.controller_interface)
        print(f"Device Controller {devpkg} imported")

# create the top level interface
toplevelinterface = DeviceInterfaceInterface(*device_interfaces)

