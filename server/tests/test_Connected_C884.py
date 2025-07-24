import unittest
from unittest import IsolatedAsyncioTestCase

from server.StageControl.PI.C884 import C884
from server.StageControl.PI.DataTypes import PIConfiguration, PIControllerModel, PIConnectionType


class TestC884(IsolatedAsyncioTestCase):

    @classmethod
    def setUpClass(self):
        pass

    async def test_connected(self):
        c1 = C884()
        await c1.updateFromConfig(PIConfiguration(
            SN=5,
            connected = True,
            model=PIControllerModel.C884,
            connection_type=PIConnectionType.rs232,
            comport=5,
            channel_amount=6,
            stages=["NOSTAGE", "NOSTAGE", "L-406.40DD10", "NOSTAGE", "NOSTAGE", "NOSTAGE"]))

        assert c1.isconnected
        c1.shutdown_and_cleanup()

if __name__ == '__main__':
    unittest.main()
