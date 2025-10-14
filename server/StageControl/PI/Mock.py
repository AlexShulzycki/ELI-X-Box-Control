from __future__ import annotations

import time

from server.StageControl.DataTypes import Notice, ConfigurationUpdate
from server.StageControl.PI.DataTypes import PIController, PIStage, PIConfiguration, PIControllerModel, PIConnectionType


class MockPIController(PIController):
    """
    PI controller that's not real, used for testing, doesn't connect to anything, but acts like one.
    """

    def __init__(self):
        super().__init__()

        # variables for simulation
        self.time_when_referenced = {}
        """Dict which stores time when a particular channel should be treated as referenced. Null if not referencing."""

    async def connect(self):
        time.sleep(0.1)
        self._config.connected = True

    async def reference(self, stages: dict[str, PIStage]):
        time.sleep(0.1)
        for stage in stages.values():
            if self.config.stages.__contains__(str(stage.channel)):
                if stage.referenced:
                    # set the referencing time to 3 seconds
                    self.time_when_referenced[stage.channel] = time.time() + 3

    async def load_stages(self, stages: dict[str, PIStage]):
        time.sleep(0.1)

        for stage in stages.values():
            if self.config.stages.__contains__(str(stage.channel)):
                self._config.stages[str(stage.channel)].device = stage.device
            else:
                self._config.stages[str(stage.channel)] = stage

    async def enable_clo(self, stages: dict[str, PIStage]):
        time.sleep(0.1)

        for stage in stages.values():
            if self.config.stages.__contains__(str(stage.channel)):
                self._config.stages[str(stage.channel)].clo = stage.clo

    async def updateFromConfig(self, config: PIConfiguration):
        # Double check that we have the correct config
        assert config.model == PIControllerModel.mock

        # Check if we are brand new
        if self.config is None:
            # ugly if then can't be bothered to streamline this
            if config.connection_type != PIConnectionType.rs232:
                self._config = PIConfiguration(
                    SN=config.SN,
                    model=config.model,
                    connection_type=config.connection_type,
                )
            else:
                self._config = PIConfiguration(
                    SN=config.SN,
                    model=config.model,
                    connection_type=config.connection_type,
                    comport=config.comport,
                    baud_rate=config.baud_rate)

        # Go through each parameter step by step
        if not self.config.connected:
            # connect
            self.EA.event(Notice(message="opening connection"))
            await self.connect()

        self.EA.event(Notice(message="loading stage names"))
        await self.load_stages(config.stages)

        self.EA.event(Notice(message="loading stage names"))
        await self.enable_clo(config.stages)

        self.EA.event(Notice(message="loading stage names"))
        await self.reference(config.stages)

        # TODO find a way to simulate this more closely
        self._config.ready = True

        # refresh full status after changing config
        await self.refreshFullStatus()

    def shutdown_and_cleanup(self):
        pass

    async def refreshFullStatus(self):
        # Send an info update, status is handled in pos on target
        for info in self.stageInfos.values():
            self.EA.event(info)

        # also refresh pos on target since this is a full refresh
        await self.refreshPosOnTarget()

    async def refreshPosOnTarget(self):
        # Send a status update
        for status in self.stageStatuses.values():
            self.EA.event(status)

    async def moveTo(self, channel: int, position: float):
        self._config.position[channel - 1] = position
        self._config.on_target[channel - 1] = True
        self.EA.event(self.stageStatuses[self.config.SN * 10 + channel])

    async def moveBy(self, channel, step: float):
        self._config.position[channel - 1] += step
        self._config.on_target[channel - 1] = True
        self.EA.event(self.stageStatuses[self.config.SN * 10 + channel])

    @property
    def config(self) -> PIConfiguration:
        return self._config

    async def is_configuration_configured(self):
        # The only PI configuration we need to query periodically for is if everything is referenced

        refstate = {}
        # go through each time when referenced for each channel
        for key, reftime in self.time_when_referenced.items():
                refstate[key] = (time.time() > reftime)

        message = "Referencing"

        for key, ref in refstate.items():
            if ref:
                # add to the message and "reference"
                message += f", Channel {key} referenced "
                # "reference"
                self._config.stages[str(key)].referenced = True

        finished = not list(refstate.values()).__contains__(False)  # if any channel is not referenced yet, don't reference

        # Construct the configuration update
        update = ConfigurationUpdate(
            SN=self.config.SN,
            message=message,
            configuration=self.config,
            finished=finished
        )

        self.EA.event(update)

        # Check if controller is ready, if True we don't need to run this function again
        return self.config.SN, finished
