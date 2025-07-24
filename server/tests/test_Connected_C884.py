import unittest

from server.StageControl.PI.C884 import C884
from server.StageControl.PI.DataTypes import PIConfiguration, PIControllerModel, PIConnectionType


class TestC884(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.c1 = C884()
        self.c1.updateFromConfig(PIConfiguration(
            SN = 5,
            model= PIControllerModel.C884,
            connection_type = PIConnectionType.rs232,
            comport = 5,
            channel_amount= 6,
            stages = ["NOSTAGE", "NOSTAGE", "L-406.40DD10", "NOSTAGE", "NOSTAGE", "NOSTAGE"]))

        assert self.c1.isconnected

    def test_connected(self):
        assert self.c1.isconnected

if __name__ == '__main__':
    unittest.main()
