import os

os.chdir("../")  # move to main server directory instead of /tests

import time
import unittest

from unittest import IsolatedAsyncioTestCase

from server.Devices.PI.DataTypes import PIConfiguration, PIControllerModel, PIConnectionType, PIStage, PIAPIConfig
from server.Devices.PI.Interface import PIControllerInterface
from server.Devices.PI.C884 import C884


class TestC884(IsolatedAsyncioTestCase):

    async def test_connected(self):
        t = time.time()
        self.c1 = C884()
        await self.c1.updateFromConfig(PIConfiguration(
            ID=118071328,
            connected=True,
            model=PIControllerModel.C884,
            connection_type=PIConnectionType.rs232,
            comport=17,
            channel_amount=4,
            stages={
                "3": PIStage(
                    channel=3,
                    device="L-406.40DD10",
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
        time.sleep(5)
        await self.c1.refreshDevices()
        print(self.c1.devices)
        print(f"moved and refreshed, took {time.time() - t}")

        self.c1.shutdown_and_cleanup()


class TestPIinterface(IsolatedAsyncioTestCase):

    async def test_basic(self):
        t = time.time()
        self.interface: PIControllerInterface = PIControllerInterface()
        await self.interface.configurationChangeRequest([PIAPIConfig(
            ID=118071328,
            model=PIControllerModel.C884,
            connection_type=PIConnectionType.rs232,
            baud_rate=115200,
            comport=17,
            stages=[
                PIStage(
                    channel=3,
                    device="L-406.40DD10",
                )
            ]
        )])
        print(f"Configured, took {time.time() - t}")
        t = time.time()
        await self.interface.refresh_configurations()
        print(f"Refreshed, took {time.time() - t}")
        await self.interface.refresh_devices()
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
