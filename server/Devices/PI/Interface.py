import asyncio
from typing import Any, Awaitable

from pydantic import BaseModel

from server.Settings import SettingsVault
from server.Devices.Interface import ControllerInterface, getComPorts
from server.Devices.DataTypes import StageStatus, StageInfo, \
    StageRemoved
from server.Devices.Events import ConfigurationUpdate, updateResponse, Notice
from server.utils.EventAnnouncer import EventAnnouncer
from server.Devices.PI.C884 import C884
from server.Devices.PI.DataTypes import PIConfiguration, PIController, PIStageInfo, PIControllerModel, \
    PIConnectionType, PIStage, PIAPIConfig
from server.Devices.PI.Mock import MockPIController


class PISettings:
    def __init__(self):
        self.EventAnnouncer = EventAnnouncer(PISettings, StageStatus, StageInfo, StageRemoved, Notice, ConfigurationUpdate)
        self._controllerStatuses = []
        # type hint, this is where we store controller statuses
        self.controllers: dict[int, PIController] = {}

    def subscribeTo(self, cntr: PIController):
        self.EventAnnouncer.patch_through_from(self.EventAnnouncer.availableDataTypes, cntr.EA)

    @property
    def currentConfiguration(self) -> list[PIConfiguration]:
        res = []
        for controller in self.controllers.values():
            res.append(controller.config)
        return res

    async def configurationChangeRequest(self, request: list[PIConfiguration]) -> list[updateResponse]:
        """
        Tries to turn the desired state into reality.
        :param request: A valid PIController status.
        :return:
        """
        res = []
        for req in request:
            try:
                # If we don't have a controller with the SN we need to create a blank new one
                if not self.controllers.keys().__contains__(req.SN):
                    await self.newController(req)
                else:
                    # Update the relevant controller

                    await self.updateController(req)
                res.append(updateResponse(
                    identifier=req.SN,
                    success=True,
                ))
            except Exception as e:
                res.append(updateResponse(
                    identifier=req.SN,
                    success=False,
                    error=str(e),
                ))

        return res

    async def removeConfiguration(self, SN: int):
        """
        Removes a controller.
        :param SN: Serial number of the controller.
        :return:
        """
        self.controllers[SN].shutdown_and_cleanup()
        self.controllers.pop(SN)

    async def newController(self, config: PIConfiguration):
        if config.model == PIControllerModel.C884:
            c884 = C884()
            await c884.updateFromConfig(config)
            self.controllers[config.SN] = c884
            self.subscribeTo(c884)
            # Do a full status refresh, which sends any new valid axis events
            await c884.refreshFullStatus()

        elif config.model == PIControllerModel.mock:
            mock = MockPIController()
            await mock.updateFromConfig(config)
            self.controllers[config.SN] = mock
            self.subscribeTo(mock)
            await mock.refreshFullStatus()
        else:
            raise Exception("Unknown PI controller model")

    def updateController(self, config: PIConfiguration) -> Awaitable:
        return self.controllers[config.SN].updateFromConfig(config)

    def getDataTypes(self) -> list[type]:
        return [PIStageInfo, PIConfiguration]

    @property
    def stageStatus(self) -> dict[int, StageStatus]:
        """Return stage status of properly configured and ready stages"""
        res = {}
        for cntrl in self.controllers.values():
            res.update(cntrl.stageStatuses)

        return res

    @property
    def stageInfo(self) -> dict[int, PIStageInfo]:
        res = {}
        for cntrl in self.controllers.values():
            res.update(cntrl.stageInfos)
        return res

    @property
    def configurationFormat(self):
        return PIConfiguration

    async def fullRefreshAllSettings(self):
        awaiters = []
        for cntr in self.controllers.values():
            awaiters.append(cntr.refreshFullStatus())

        await asyncio.gather(*awaiters)


def deconstruct_SN_Channel(sn_channel):
    """
    Extracts the channel and serial number from a unique serial-number-channel identifier
    :param sn_channel: serial number with the channel glued to the end
    :return: serial number and channel, separately!
    """
    channel: int = sn_channel % 10  # modulo 10 gives last digit
    sn: int = int((sn_channel - channel) / 10)  # minus channel, divide by 10 to get rid of 0
    return sn, channel


class PIControllerInterface(ControllerInterface):

    async def configurationChangeRequest(self, request: list[PIAPIConfig]) -> list[updateResponse]:
        """Received a configuration change in PIAPI form"""
        # lets convert to PIConfiguration objects we can use
        configlist = []
        for req in request:
            configlist.append(req.toPIConfig())
        return await self.settings.configurationChangeRequest(configlist)

    async def removeConfiguration(self, id: int):
        return await self.settings.removeConfiguration(id)

    @property
    def currentConfiguration(self) -> list[PIAPIConfig]:
        """Returns current configurations in API-ready form"""
        PIConfigs: list[PIConfiguration] = self.settings.currentConfiguration
        # just converting to PIAPI, which plays nice with json schemas.
        res = []
        for config in PIConfigs:
            res.append(config.toPIAPI())
        return res

    @property
    def configurationType(self) -> BaseModel:
        return PIAPIConfig

    @property
    async def configurationSchema(self):
        """
        Generate a JSON schema of the configuration object that is sufficiently descriptive and exhaustive.
        :return: JSON schema that describes the PI configuration object.
        """
        # Grab the JSON schema from the pydantic object
        schema = self.configurationType.model_json_schema()


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
        for config in self.settings.currentConfiguration:
            if config.connection_type == PIConnectionType.rs232:
                coms.append(config.comport)


        schema["properties"]["comport"]["enum"] = coms

        return schema

    async def fullRefreshAllSettings(self):
        return await self.settings.fullRefreshAllSettings()

    async def moveBy(self, identifier: int, step: float):
        sn, channel = deconstruct_SN_Channel(identifier)
        await self.settings.controllers[sn].moveBy(channel, step)

    def __init__(self):
        super().__init__()
        self._settings: PISettings = PISettings()
        """The PISettings is handling basically everything for us"""
        self.EventAnnouncer.patch_through_from(self.EventAnnouncer.availableDataTypes, self.settings.EventAnnouncer)
        self.SV = SettingsVault()

    @property
    def settings(self) -> PISettings:
        return self._settings

    @property
    def stages(self) -> list[int]:
        res = []
        for info in self.settings.stageInfo.values():
            res.append(info.identifier)

        return res

    async def moveTo(self, identifier: int, position: float):
        sn, channel = deconstruct_SN_Channel(identifier)
        await self.settings.controllers[sn].moveTo(channel, position)

    @property
    def stageInfo(self) -> dict[int, StageInfo]:
        res = {}
        for info in self.settings.stageInfo.values():
            res[info.identifier] = info
        return res

    def getAllControllerSNs(self) -> list[int]:
        sns: list[int] = []
        for cntrl in self.settings.controllers.keys():
            sns.append(cntrl)
        return sns

    def getRelevantControllerSNs(self, identifiers: list[int] = None) -> list[int]:
        """
        Grabs all identifiers of relevant controllers for the given identifier list. If no list provided, returns all controllers.
        :param identifiers: Identifiers we want the controllers for
        :return:
        """
        controller_sn: list[int] = []
        if identifiers is None:
            # grab all serial numbers if none
            controller_sn = self.getAllControllerSNs()
        else:
            for idnt in identifiers:
                sn, channel = deconstruct_SN_Channel(idnt)
                if not controller_sn.__contains__(sn):
                    controller_sn.append(sn)
        return controller_sn

    async def updateStageInfo(self, identifiers: list[int] = None):
        """
        Do a full refresh of each controller's status.
        :param identifiers: identifiers of stages we want to update
        """
        controller_sn = self.getRelevantControllerSNs(identifiers)

        # run it async and call it a day
        awaiters = []
        for sn in controller_sn:
            awaiters.append(self.settings.controllers[sn].refreshFullStatus())
        await asyncio.gather(*awaiters)

    @property
    def stageStatus(self) -> dict[int, StageStatus]:
        res = {}
        for stat in self.settings.stageStatus.values():
            res[stat.identifier] = stat
        return res

    async def updateStageStatus(self, identifiers: list[int] = None):
        """
        Refresh position and ontarget of the given identifiers' controllers.
        :param identifiers: SN-Channel combo identifier
        :return:
        """
        controller_sn = self.getRelevantControllerSNs(identifiers)

        # run it async and call it a day
        awaiters = []
        for sn in controller_sn:
            # only if we have this identifier, of course
            if self.settings.controllers.keys().__contains__(sn):
                awaiters.append(self.settings.controllers[sn].refreshPosOnTarget())
        await asyncio.gather(*awaiters)

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
        for identifier, controller in self.settings.controllers.items():
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
