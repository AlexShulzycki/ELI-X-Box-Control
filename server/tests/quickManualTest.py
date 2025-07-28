import unittest
from fastapi.testclient import TestClient

from server.StageControl.PI.C884 import C884RS232Config, C884Config
from server.main import app
from server.API.SettingsAPI import StageConfig


client = TestClient(app)


class ManualC884Test(unittest.TestCase):
    """
    Test with a connected c884 controller via usb
    """

    @classmethod
    def setUpClass(self):
        # connect
        #request = client.get(f"/pi/Connect/{self.SN}") THIS IS FOR USB
        config = C884RS232Config(
            comport = 4
        )
        request = client.post("/pi/AddRS232", json = config.model_dump())
        self.SN = int(request.text)
        assert request.status_code == 200

        #self.SN = 425003044
        """Serial number of the controller"""

        # config
        stageconfig = StageConfig(C884=[C884Config(serial_number=self.SN, stages=["NOSTAGE"] * 6)])
        stageconfig.C884[0].stages[5] = "M-414.2DG"
        request = client.post("/post/UpdateConfig/", json=stageconfig.model_dump())
        assert request.status_code == 200

        # load settings onto C884
        request = client.get(f"/pi/LoadStagesToC884/{self.SN}/")
        assert request.status_code == 200

        # startup CLO
        serial_number_axis = self.SN * 10 + 6
        request = client.get(f"/pi/enableCLO/{serial_number_axis}/")
        assert request.status_code == 200

        print(client.get(f"/pi/Status/").json)
    @classmethod
    def tearDownClass(self):
        client.get(f"pi/RemoveBySerialNumber/{self.SN}")

    def test_supported_stages(self):
        request = client.get(f"pi/supportedStages/{self.SN}")
        assert request.status_code == 200
        print(f"Received {len(request.json())} stages")

    def test_minmax(self):
        request = client.get(f"/pi/getRange/{self.SN}")
        assert request.status_code == 200
        print(request.json())

    def test_stages_connected(self):
        request = client.get(f"/stage/allstageinfo")
        assert request.status_code == 200
        print(request.text)

if __name__ == '__main__':
    unittest.main()
