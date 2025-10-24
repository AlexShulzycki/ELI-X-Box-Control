import asyncio
from typing import Any, Awaitable

from pydantic import BaseModel

import server.utils
from server.Devices import Configuration, RotationalStageDevice
from server.Devices import Device, LinearStageDevice
from server.Settings import SettingsVault
from server.Devices.Interface import ControllerInterface, getComPorts
from server.Devices.Events import ConfigurationUpdate, updateResponse, Notice, ActionRequest
from server.Devices.PI.C884 import C884
from server.Devices.PI.DataTypes import PIConfiguration, PIController, PIControllerModel, \
    PIConnectionType, PIStage, PIAPIConfig
from server.Devices.PI.Mock import MockPIController


class PIControllerInterface(ControllerInterface):

    def __init__(self):
        super().__init__()
        self.controllers: dict[int, PIController] = {}
        self.SV = SettingsVault()

    @property
    def devices(self) -> list[Device]:
        res = []
        for cntrl in self.controllers.values():
            res.extend(list(cntrl.devices.values()))
        return res

    async def execute_action(self, action: ActionRequest) -> None:
        # find the correct controller
        for cntrl in self.controllers.values():
            if action.device_id in cntrl.devices.keys():
                cntrl.execute_action(action)

    @property
    def device_schemas(self) -> list[dict[str, Any]]:
        res = []
        for dv in [LinearStageDevice, RotationalStageDevice]:
            res.append(dv.model_json_schema())
        return res

    @property
    def configurationPydanticModel(self):
        return PIAPIConfig

    @property
    def currentConfigurations(self) -> list[PIConfiguration]:
        """Returns current configurations in API-ready form"""
        res = []
        for controller in self.controllers.values():
            res.append(controller.config.toPIAPI())
        return res

    async def refresh_devices(self, ids: list[int] | None = None) -> list[int]:
        """
        Refreshes data relevant to stages, like position, ontarget, referenced status.
        """
        # First we need to make a list of PIController objects we need refreshed.
        to_refresh: list[int] = []
        for ID in ids:
            sn, channel = PIController.deconstruct_SN_Channel(ID)
            # double check that we have this controller, append to the list if not already there
            if sn in self.configurationIDs and sn not in to_refresh:
                to_refresh.append(sn)

        # ask each controller to kindly refresh
        awaitables = []
        for ID in to_refresh:
            awaitables.append(self.controllers[ID].refreshDevices())
        # flatten results
        return await server.utils.gather_and_flatten(awaitables)

    async def refresh_configurations(self, ids: list[int] | None = None) -> None:
        # TODO do this selectively based on ID
        awaiters = []
        for cntr in self.controllers.values():
            awaiters.append(cntr.refreshFullStatus())

        await asyncio.gather(*awaiters)

    async def configurationChangeRequest(self, requests: list[PIAPIConfig]) -> list[updateResponse]:
        """
        Tries to turn the desired state into reality.
        :param requests: Valid PIController statuses.
        :return:
        """

        res = []
        for request in requests:
            req = request.toPIConfig()
            try:
                # If we don't have a controller with the SN we need to create a blank new one
                if not self.controllers.keys().__contains__(req.ID):
                    await self.newController(req)
                else:
                    # Update the relevant controller

                    await self.updateController(req)
                res.append(updateResponse(
                    identifier=req.ID,
                    success=True,
                ))
            except Exception as e:
                res.append(updateResponse(
                    identifier=req.ID,
                    success=False,
                    error=str(e),
                ))

        return res

    async def newController(self, config: PIConfiguration):
        if config.model == PIControllerModel.C884:
            c884 = C884()
            await c884.updateFromConfig(config)
            self.controllers[config.ID] = c884
            self.EventAnnouncer.patch_through_from(self.EventAnnouncer.availableDataTypes, c884.EA)
            # Do a full status refresh, which sends any new valid axis events
            await c884.refreshFullStatus()

        elif config.model == PIControllerModel.mock:
            mock = MockPIController()
            await mock.updateFromConfig(config)
            self.controllers[config.ID] = mock
            self.EventAnnouncer.patch_through_from(self.EventAnnouncer.availableDataTypes, mock.EA)
            await mock.refreshFullStatus()
        else:
            raise Exception("Unknown PI controller model")

    def updateController(self, config: PIConfiguration) -> Awaitable:
        return self.controllers[config.ID].updateFromConfig(config)

    async def removeConfiguration(self, ID: int):
        """
        Removes a controller.
        :param ID: Serial number of the controller.
        :return:
        """
        self.controllers[ID].shutdown_and_cleanup()
        self.controllers.pop(ID)

    @property
    async def configurationSchema(self):
        """
        Generate a JSON schema of the configuration object that is sufficiently descriptive and exhaustive.
        :return: JSON schema that describes the PI configuration object.
        """
        # Grab the JSON schema from the pydantic object
        schema = self.configurationPydanticModel.model_json_schema()

        # Enforce requirements for RS232
        schema["if"] = {
            "properties": {
                "connection_type": {
                    "enum": [PIConnectionType.rs232]
                }
            }
        }
        schema["then"] = {
            "required": ["baud_rate", "comport"]
        }

        # turn the PIStage device field into a dropdown
        # Update from settings

        await self.SV.reload_all()
        schema["$defs"]["PIStage"]["properties"]["device"]["enum"] = list(self.SV.readonly["PIStages"].keys())

        # turn the comport field into a dropdown
        # grab free comports
        coms = getComPorts()
        # add comport 0 to allow for the default value
        coms.append(0)

        # add connected comports so the controller doesn't throw a fit
        for config in self.currentConfigurations:
            if config.connection_type == PIConnectionType.rs232:
                coms.append(config.comport)

        schema["properties"]["comport"]["enum"] = coms

        return schema

    async def moveBy(self, identifier: int, step: float):
        sn, channel = PIController.deconstruct_SN_Channel(identifier)
        await self.controllers[sn].moveBy(channel, step)

    async def moveTo(self, identifier: int, position: float):
        sn, channel = PIController.deconstruct_SN_Channel(identifier)
        await self.controllers[sn].moveTo(channel, position)

    @property
    def name(self) -> str:
        return "PI"

    async def is_configuration_configured(self, identifiers: list[int]) -> list[int]:
        """
        Checks if we have a controller with the given SN, and returns is_configuration_configured.
        :param identifiers:
        :return:
        """

        # Ask each controller
        awaiters: list[Awaitable[tuple[int, bool]]] = []
        for identifier, controller in self.controllers.items():
            if identifier in identifiers:
                # Check if it's the correct identifier, if so append to awaiters
                awaiters.append(controller.is_configuration_configured())

        awaited: list[tuple[int, bool]] = await asyncio.gather(*awaiters)
        res = []
        # Go through each awaiter and construct a response array
        for SN, finished in awaited:
            if not finished:
                res.append(SN)
        return res
