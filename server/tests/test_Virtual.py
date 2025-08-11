import asyncio
from unittest.async_case import IsolatedAsyncioTestCase

from server.StageControl.DataTypes import StageInfo
from server.StageControl.Virtual import VirtualControllerInterface


class TestVirtualControllerInterface(IsolatedAsyncioTestCase):

    @classmethod
    def setUp(self):
        self.vinterface = VirtualControllerInterface()
        config1 = StageInfo(
            identifier=1,
            model="virtual"
        )
        config2 = StageInfo(
            identifier=2,
            model="virtual",
            minimum=0,
            maximum=100
        )

        asyncio.shield(asyncio.wait_for(self.vinterface.configurationChangeRequest([config1, config2]), 2))

    def test_stages(self):
        assert self.vinterface.stages.__contains__(1)

    async def test_move_to(self):
        await self.vinterface.moveTo(1, 25)
        # TODO Finish implementing the update simulation
        # make sure that it only updates when we run the update function
        #assert self.vinterface.stageStatus[1].position == 0
        await self.vinterface.updateStageStatus()
        assert self.vinterface.stageStatus[1].position == 25

    async def test_remove_stage(self):
        await self.vinterface.settings.removeConfiguration(1)
        await self.vinterface.settings.removeConfiguration(2)
        assert self.vinterface.stages == []
        assert self.vinterface.stageStatus == {}
        assert self.vinterface.stageInfo == {}