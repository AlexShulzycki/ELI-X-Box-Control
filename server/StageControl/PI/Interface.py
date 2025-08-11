import asyncio
from typing import Any, Awaitable

from pydantic import BaseModel

from server.StageControl.DataTypes import ControllerInterface, StageStatus, StageInfo, \
    updateResponse, StageRemoved, EventAnnouncer
from server.StageControl.PI.C884 import C884
from server.StageControl.PI.DataTypes import PIConfiguration, PIController, PIStageInfo, PIControllerModel, \
    MockPIController


class PISettings:
#TODO IMPLEMENT STAGEREMOVED self.EventAnnouncer.event(StageRemoved(identifier = identifier))
    def __init__(self):
        self.EventAnnouncer = EventAnnouncer(StageStatus, StageInfo, StageRemoved)
        self._controllerStatuses = []
        # type hint, this is where we store controller statuses
        self.controllers: dict[int, PIController] = {}

    def subscribeTo(self, cntr: PIController):
        sub = cntr.EA.subscribe(StageStatus, StageInfo, StageRemoved)
        sub.deliverTo(StageStatus, self.EventAnnouncer.event)
        sub.deliverTo(StageInfo, self.EventAnnouncer.event)
        sub.deliverTo(StageRemoved, self.EventAnnouncer.event)

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
            self.subscribeTo(mock)
            self.controllers[config.SN] = mock
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

    async def configurationChangeRequest(self, request: list[Any]) -> list[updateResponse]:
        return await self.settings.configurationChangeRequest(request)

    async def removeConfiguration(self, id: int):
        return await self.settings.removeConfiguration(id)

    @property
    def currentConfiguration(self) -> list[PIConfiguration]:
        return self.settings.currentConfiguration

    @property
    async def configurationFormat(self):
        return self.settings.configurationFormat.model_json_schema()

    async def fullRefreshAllSettings(self):
        return await self.settings.fullRefreshAllSettings()

    async def moveBy(self, identifier: int, step: float):
        sn, channel = deconstruct_SN_Channel(identifier)
        await self.settings.controllers[sn].moveBy(channel, step)

    def __init__(self):
        super().__init__()
        self._settings:PISettings = PISettings()
        """The PISettings is handling basically everything for us"""
        self.EventAnnouncer.patch_through_from(self.EventAnnouncer.availableDataTypes, self.settings.EventAnnouncer)

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
            awaiters.append(self.settings.controllers[sn].refreshPosOnTarget())
        await asyncio.gather(*awaiters)


    @property
    def name(self) -> str:
        return "PI"


    async def bulkCommand(self, serial_number_channel: list[int], command) -> Awaitable[list[Any]]:
        """
        Execute a getter command efficiently across available C884s
        :param serial_number_channel: identifier of the axes we want to work with
        :param command: command we want to issue, from the C884 object
        :return: results in the same order as the axes identifiers were given
        """
        # Avoid making redundant requests, extract as much info as possible
        # Round up the controller serial numbers, create empty dict
        controllers = {}
        for sc in serial_number_channel:
            sn, ch = self.deconstruct_Serial_Channel(sc)
            controllers[sn] = []
        print(controllers)
        # Iterate through each controller serial number in the dict
        for cntr_sn in controllers:
            controllers[cntr_sn]: Awaitable[list[Any]] = command(self.c884[cntr_sn])  # this returns a coroutine!!!

        # Finally, iterate through the request array again and create a parallel response array
        res: list[Any] = []
        for sn_ch in serial_number_channel:
            sn, ch = self.deconstruct_Serial_Channel(sn_ch)

            # await if we have to
            solution = controllers[sn]
            print(type(solution))
            if isinstance(solution, Coroutine):
                controllers[sn] = await solution

            # the relevant dict entry now contains the solution
            res.append((controllers[sn])[ch -1]) # we only want the relevant channel, -1 to get the index.

        res: Awaitable[list[Any]] # make sure to hint that it's an awaitable
        return res