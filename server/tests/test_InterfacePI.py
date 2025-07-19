from unittest import TestCase

from server.StageControl.PI.DataTypes import PISettings, PIControllerStatus, PIControllerModel, PIConnectionType


class TestPISettings(TestCase):

    @classmethod
    def setUp(self):
        pass


class TestPIControllerStatus(TestCase):

    @classmethod
    def setUp(self):
        pass

    def test_basic(self):
        try:
            usb = PIControllerStatus(
                SN=1,
                model=PIControllerModel.C884,
                connection_type= PIConnectionType.usb,
                connected = True,
                channel_amount=1,
                ready = False,
                referenced= [True],
                clo = [True],
                stages = ["NOSTAGE"]
            )
        except:
            self.fail()

    def test_incorrect_channel_amount(self):
        with self.assertRaises(ValueError):
            # channel_amount is wrong
            usb = PIControllerStatus(
                SN=1,
                model=PIControllerModel.C884,
                connection_type= PIConnectionType.usb,
                connected = True,
                channel_amount=7,
                ready = False,
                referenced= [True],
                clo = [True],
                stages = ["NOSTAGE"]
            )

            # One of the arrays has the wrong size
            usb = PIControllerStatus(
                SN=1,
                model=PIControllerModel.C884,
                connection_type= PIConnectionType.usb,
                connected = True,
                channel_amount=1,
                ready = False,
                referenced= [True, False],
                clo = [True],
                stages = ["NOSTAGE"]
            )


