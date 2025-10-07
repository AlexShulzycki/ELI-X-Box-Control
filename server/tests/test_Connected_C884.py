import time
import unittest
from unittest import IsolatedAsyncioTestCase

from server.Interface import PIinterface
from server.StageControl.PI.C884 import C884
from server.StageControl.PI.DataTypes import PIConfiguration, PIControllerModel, PIConnectionType, PIStage
from server.StageControl.PI.Interface import PIControllerInterface


class TestC884(IsolatedAsyncioTestCase):

    async def test_connected(self):
        t = time.time()
        self.c1 = C884()
        await self.c1.updateFromConfig(PIConfiguration(
            SN=118071328,
            connected=True,
            model=PIControllerModel.C884,
            connection_type=PIConnectionType.rs232,
            comport=17,
            channel_amount=4,
            stages = {
                "3": PIStage(
                    channel=3,
                    device= "L-406.40DD10",

                )
            }))

        print(f"Configured, took {time.time() - t}")
        t = time.time()
        await self.c1.refreshFullStatus()
        print(f"Refreshed, took {time.time() - t}")
        config = self.c1.config
        print(config)
        assert self.c1.isconnected
        t = time.time()
        config.stages["3"].referenced = True
        config.stages["3"].clo = True
        await self.c1.updateFromConfig(config)
        print(f"Updated, took {time.time() - t}")
        time.sleep(5)
        t = time.time()
        await self.c1.refreshFullStatus()
        print(f"Refreshed, took {time.time() - t}")
        print(self.c1.config)
        time.sleep(2)
        t = time.time()
        await self.c1.moveTo(3, 30)
        await self.c1.refreshPosOnTarget()
        print(self.c1.stageStatuses)
        print(f"moved and refreshed, took {time.time() - t}")

        self.c1.shutdown_and_cleanup()


class TestPIinterface(IsolatedAsyncioTestCase):

    async def test_basic(self):
        t = time.time()
        self.interface:PIControllerInterface = PIinterface
        await self.interface.settings.configurationChangeRequest([PIConfiguration(
            SN=425003044,
            connected=True,
            model=PIControllerModel.C884,
            connection_type=PIConnectionType.rs232,
            comport=5,
            channel_amount=6,
            stages=["NOSTAGE", "NOSTAGE", "L-406.40DD10", "NOSTAGE", "NOSTAGE", "NOSTAGE"])])
        print(f"Configured, took {time.time() - t}")
        t = time.time()
        await self.interface.settings.fullRefreshAllSettings()
        print(f"Refreshed, took {time.time() - t}")
        config = self.interface.settings.currentConfiguration[0]
        print(config)
        assert config.connected
        config.referenced = [None, None, True, None, None, None]
        config.clo = [None, None, True, None, None, None]
        t = time.time()
        await self.interface.settings.configurationChangeRequest([config])
        print(f"Updated, took {time.time() - t}")
        time.sleep(5)
        t = time.time()
        await self.interface.settings.fullRefreshAllSettings()
        print(f"Refreshed, took {time.time() - t}")
        print(self.interface.settings.currentConfiguration[0])
        time.sleep(2)
        t = time.time()
        await self.interface.moveTo(config.SN * 10 + 3, 20)
        await self.interface.settings.fullRefreshAllSettings()
        print(self.interface.stageStatus)
        print(f"moved and refreshed, took {time.time() - t}")

        await self.interface.settings.removeConfiguration(config.SN)

if __name__ == '__main__':
    unittest.main()
