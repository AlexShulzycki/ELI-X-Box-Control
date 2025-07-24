import asyncio
import unittest
from unittest import IsolatedAsyncioTestCase

from server.StageControl.PI.C884 import C884
from server.StageControl.PI.DataTypes import PIConfiguration, PIControllerModel, PIConnectionType


class TestC884(IsolatedAsyncioTestCase):

    async def test_connected(self):
        self.c1 = C884()
        await self.c1.updateFromConfig(PIConfiguration(
            SN=425003044,
            connected=True,
            model=PIControllerModel.C884,
            connection_type=PIConnectionType.rs232,
            comport=5,
            channel_amount=6,
            stages=["NOSTAGE", "NOSTAGE", "L-406.40DD10", "NOSTAGE", "NOSTAGE", "NOSTAGE"]))
        print("Configured")
        await self.c1.refreshFullStatus()
        config = self.c1.config
        print(config)
        assert self.c1.isconnected
        config.referenced = [None, None, True, None, None, None]
        await self.c1.updateFromConfig(config)

    async def test_FRF(self):
        await self.c1.refreshFullStatus()
        print(self.c1.config)

    @classmethod
    async def tearDownClass(self):
        await self.c1.shutdown_and_cleanup()
if __name__ == '__main__':
    unittest.main()
