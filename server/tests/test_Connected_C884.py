import time
import unittest
from unittest import IsolatedAsyncioTestCase

from server.StageControl.PI.C884 import C884
from server.StageControl.PI.DataTypes import PIConfiguration, PIControllerModel, PIConnectionType


class TestC884(IsolatedAsyncioTestCase):

    async def test_connected(self):
        t = time.time()
        self.c1 = C884()
        await self.c1.updateFromConfig(PIConfiguration(
            SN=425003044,
            connected=True,
            model=PIControllerModel.C884,
            connection_type=PIConnectionType.rs232,
            comport=5,
            channel_amount=6,
            stages=["NOSTAGE", "NOSTAGE", "L-406.40DD10", "NOSTAGE", "NOSTAGE", "NOSTAGE"]))
        print(f"Configured, took {time.time() - t}")
        t = time.time()
        await self.c1.refreshFullStatus()
        print(f"Refreshed, took {time.time() - t}")
        config = self.c1.config
        print(config)
        assert self.c1.isconnected
        config.referenced = [None, None, True, None, None, None]
        config.clo = [None, None, True, None, None, None]
        t = time.time()
        await self.c1.updateFromConfig(config)
        print(f"Updated, took {time.time() - t}")
        t = time.time()
        #await self.c1.setServoCLO([None, None, True, None, None, None])
        #await self.c1.reference([None, None, True, None, None, None])
        await self.c1.refreshFullStatus()
        print(f"Refreshed, took {time.time() - t}")
        print(self.c1.config)
        time.sleep(2)
        t = time.time()
        await self.c1.moveTo(3, 20)
        await self.c1.refreshPosOnTarget()
        print(self.c1.stageStatuses)
        print(f"moved and refreshed, took {time.time() - t}")

    @classmethod
    async def tearDownClass(self):
        await self.c1.shutdown_and_cleanup()
if __name__ == '__main__':
    unittest.main()
