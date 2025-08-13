import asyncio
import time
from typing import Awaitable

import libximc.highlevel as ximc

from server.Settings import SettingsVault
from server.StageControl.DataTypes import ControllerInterface, StageStatus, StageInfo, \
    updateResponse, Notice
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
            return

        awaiters = []
        for ident in identifiers:
            if self.stages.__contains__(ident):
                awaiters.append(self.refreshConfig(ident))

        await asyncio.gather(*awaiters)

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
                Calibration=item["Calibration"],
                MinMax=item["MinMax"],
                Kind=item["Kind"]
            )

        self.StandaSettings = stageconfigs

    async def handleConfig(self, request: StandaConfiguration) -> updateResponse:
        """
        Handles a configuration request for the given ximc device. Device must already be in self.ximcs
        :param request: Config to handle
        :return:
        """
        device = self.ximcs[request.SN]
        config = self._configs[request.SN]
        status = None
        try:
            config.connected = False
            # we have no way to check if we are currently connected (yippee)
            # so we try to get status, if we can't, then we are probably not connected.
            # incredible implementation by the team at ximc
            try:
                device.get_status()
            except:
                # error, probably not connected
                device.open_device()

            status = device.get_status()
            # if we make it here we are connected
            config.connected = True
            # set calibration
            device.set_calb(self.StandaSettings[request.model].Calibration, device.get_engine_settings().MicrostepMode)
        except Exception as e:
            config.connected = False
            return updateResponse(
                identifier=request.SN,
                success=False,
                error=f"Unable to connect to Standa device, SN {config.SN}, error: {e}"
            )
        # we have not failed to connect
        # minmax is not sent to the controller
        self._configs[request.SN].min_max = request.min_max

        # Check if homed and if we want it homed
        if not status.Flags.__contains__(ximc.StateFlags.STATE_IS_HOMED) and request.homed:
            # let the user know we're homing
            self.EventAnnouncer.event(Notice(
                identifier=request.SN,
                message="Connected, homing to zero position..."
            ))
            await asyncio.sleep(0.1)  # give some time for the request to send
            try:
                device.command_homezero()
                config.homed = True
            except:
                # TODO error handling
                config.homed = False

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
                return

        # if we are here, no such serial number was found.
        raise Exception(f"No Standa device found under serial number {SN}")

    async def configurationChangeRequest(self, request: list[StandaConfiguration]) -> list[updateResponse]:
        # Check if this is the first config request, if so then make use of the async status
        # to read in StandaStage presets
        if len(self.StandaSettings) == 0:
            await self.loadStandaSettings()

        # quickly probe for all connected ximc devices
        devices = ximc.enumerate_devices(ximc.EnumerateFlags.ENUMERATE_PROBE)
        awaiters: list[Awaitable[updateResponse]] = []
        # handle config change requests
        res: list[updateResponse] = []
        for req in request:
            if req.SN not in self.ximcs.keys():
                try:
                    self.addNewDevice(req.SN, req.model, devices)
                except Exception as e:
                    res.append(updateResponse(identifier=req.SN, success=False, error=str(e)))
                    continue
            awaiters.append(self.handleConfig(req))
        res = res + (await asyncio.gather(*awaiters))

        # let's now do a full refresh before returning results
        await self.fullRefreshAllSettings()
        return res

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
                kind=self.StandaSettings[c.model].Kind,
                minimum=c.min_max[0],
                maximum=c.min_max[1]
            )
        return res

    @property
    def configurationType(self):
        return StandaConfiguration

    @property
    async def configurationSchema(self):
        # modify the generated schema by enum-ing the model field
        schema =  StandaConfiguration.model_json_schema()
        await self.loadStandaSettings()
        schema["properties"]["model"]["enum"] = list(self.StandaSettings.keys())
        # now we check which serial numbers are available
        sns = []

        # WE HAVE TO PUT THIS AS THE FIRST ENTRY IN THE ARRAY
        # append a type: integer catch-all schema in case the server returns a serial number
        # not in the rest of the anyOf array and causes a schema validator to have a fit, like when
        # the currently connected stage does not show up in the anyOf due to the virtue of
        # it already being connected.
        sns.append({
            "type": "integer",
        })


        for dev in ximc.enumerate_devices(ximc.EnumerateFlags.ENUMERATE_PROBE):
            sns.append({
                "const": dev['device_serial'],
                "title": dev['ControllerName']})


        schema["properties"]["SN"]["anyOf"] = sns
        return schema

    async def refreshConfig(self, SN: int):

        initialstageinfo = self.stageInfo[SN]
        initialstagestatus = self.stageStatus[SN]

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
            newconfig.homed = False
            newconfig.ontarget = True # to prevent infinite loop continuously checking for updates

        self._configs[SN] = newconfig

        # event announcing
        if self.stageInfo[SN] != initialstageinfo:
            self.EventAnnouncer.event(self.stageInfo[SN])
        if self.stageStatus[SN] != initialstagestatus:
            self.EventAnnouncer.event(self.stageStatus[SN])

    async def fullRefreshAllSettings(self):
        """All we do is check the position and on target status"""
        awaiters = []
        for conf in self.currentConfiguration:
            awaiters.append(self.refreshConfig(conf.SN))
        await asyncio.gather(*awaiters)

