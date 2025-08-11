import asyncio
from typing import Awaitable
from pydantic import BaseModel

import libximc.highlevel as ximc

from server.Settings import SettingsVault
from server.StageControl.DataTypes import ControllerInterface, StageStatus, StageInfo, \
    updateResponse, StageKind
from server.StageControl.Standa.DataTypes import StandaStage, StandaConfiguration


class StandaInterface(ControllerInterface):

    def __init__(self):
        super().__init__()
        self.ximcs: dict[int, ximc.Axis] = {}
        self._configs: dict[int, StandaConfiguration] = {}
        self.StandaSettings: dict[str, StandaStage] = {}

    @property
    def stages(self) -> list[int]:
        return list(self.stageInfo.keys())

    async def moveTo(self, identifier: int, position: float):
        self.ximcs[identifier].command_move_calb(position)

    async def moveBy(self, identifier: int, step: float):
        self.ximcs[identifier].command_movr_calb(step)

    async def updateStageInfo(self, identifiers: list[int] = None):
        if identifiers is None:
            await self.fullRefreshAllSettings()

        awaiters = []
        for ident in identifiers:
            awaiters.append(self.refreshConfig(ident))

    async def updateStageStatus(self, identifiers: list[int] = None):
        await self.updateStageInfo(identifiers)

    @property
    def name(self) -> str:
        return "Standa"

    @property
    def currentConfiguration(self) -> list[StandaConfiguration]:
        return list(self._configs.values())

    async def loadStandaSettings(self):
        SV = SettingsVault()
        await SV.load_all()
        stageconfigs = {}
        for key, item in dict(SV.readonly["StandaStages"]).items():
            stageconfigs[key] = StandaStage(
                Name=key,
                Calibration=item.Calibration,
                MinMax=item.MinMax,
                Kind=StageKind(item.Kind)
            )

        self.StandaSettings = stageconfigs

    async def handleConfig(self, request: StandaConfiguration) -> updateResponse:
        """
        Handles a configuration request for the given ximc device. Device must already be in self.ximcs
        :param request: Config to handle
        :return:
        """
        device = self.ximcs[request.SN]
        config = self._configs[request.sn]
        status = None
        try:
            device.open_device()
            status = device.get_status()
        except:
            config.connected = False
            return updateResponse(
                identifier=request.SN,
                success=False,
                error=f"Unable to connect to Standa device, SN {config.SN}"
            )
        # we have not failed to connect
        # minmax or stage type is not sent to the controller
        self._configs[request.sn].min_max = request.min_max
        self._configs[request.sn].kind = request.kind

        # Check if homed and if we want it homed
        if not status.Flags.__contains__(ximc.StateFlags.STATE_IS_HOMED) and request.homed:
            device.command_homezero()

        # return update response
        return updateResponse(success=True, identifier=request.SN)

    def addNewDevice(self, SN: int, model: str, devices: list[dict]):
        """Adds a new XIMC device along with an empty config to self.ximcs and self._configs"""
        for dev in devices:
            if dev["device_serial"] == SN:
                self.ximcs[SN] = ximc.Axis(dev["uri"])
        self._configs[SN] = StandaConfiguration(
            SN=SN,
            model=model,
            min_max=self.StandaSettings[model].MinMax,  # for now
        )

    async def configurationChangeRequest(self, request: list[StandaConfiguration]) -> list[updateResponse]:
        # Check if this is the first config request, if so then make use of the async status
        # to read in StandaStage presets
        if len(self.StandaSettings) == 0:
            await self.loadStandaSettings()

        # quickly probe for all connected ximc devices
        devices = ximc.enumerate_devices(ximc.EnumerateFlags.ENUMERATE_PROBE)
        awaiters: list[Awaitable[updateResponse]] = []
        # handle config change requests
        for req in request:
            if req.SN not in self.ximcs.keys():
                self.addNewDevice(req.SN, req.calibration, devices)
            awaiters.append(self.handleConfig(req))

        return await asyncio.gather(*awaiters)

    async def removeConfiguration(self, SN: int):
        if self.ximcs.keys().__contains__(SN):
            self.ximcs[SN].close_device()
            del self.ximcs[SN]
            del self._configs[SN]
            return True
        else:
            return False

    @property
    def stageStatus(self) -> dict[int, StageStatus]:
        res = {}
        for c in self.currentConfiguration:
            res[c.SN] = StageStatus(
                identifier=c.SN,
                connected=c.connected,
                ready=c.homed and c.connected,
                position=c.position,
                ontarget=c.ontarget
            )
        return res

    @property
    def stageInfo(self) -> dict[int, StageInfo]:
        res = {}
        for c in self.currentConfiguration:
            res[c.SN] = StageInfo(
                model=c.model,
                identifier=c.SN,
                kind=c.kind,
                minimum=c.min_max[0],
                maximum=c.min_max[1]
            )
        return res

    @property
    def configurationFormat(self) -> BaseModel:
        return StandaConfiguration

    async def refreshConfig(self, SN: int):
        status = None
        newconfig = self._configs[SN]
        try:
            status = self.ximcs[SN].get_status()
            newconfig.connected = True
            if status.Flags.__contains__(ximc.StateFlags.STATE_IS_HOMED):
                newconfig.homed = True
            else:
                newconfig.homed = False

            newconfig.ontarget = not str(self.ximcs[SN].get_status().MvCmdSts).__contains__("MVCMD_RUNNING")
            newconfig.position = self.ximcs[SN].get_position_calb().Position

        except:
            newconfig.connected = False
            newconfig.ready = False

        self._configs[SN] = newconfig

    async def fullRefreshAllSettings(self):
        """All we do is check the position and on target status"""
        awaiters = []
        for conf in self.currentConfiguration:
            awaiters.append(self.refreshConfig(conf.SN))
        await asyncio.gather(*awaiters)

