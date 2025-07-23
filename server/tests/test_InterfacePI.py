from unittest import TestCase, IsolatedAsyncioTestCase

from server.StageControl.PI.DataTypes import PIConfiguration, PIControllerModel, PIConnectionType
from server.StageControl.PI.Interface import PIControllerInterface


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
            usb = PIConfiguration(
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
            usb = PIConfiguration(
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
            usb = PIConfiguration(
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
    def test_initialize_pos_ont(self):
        usb = PIConfiguration(
            SN=1,
            model=PIControllerModel.C884,
            connection_type=PIConnectionType.usb,
            connected=True,
            channel_amount=2,
            ready=False,
            referenced=[True, False],
            clo=[True, False],
            stages=["NOSTAGE", "weewoo"]
        )

class TestMockC884(IsolatedAsyncioTestCase):
    # not a very good test because the mock C884 is not very good either
    @classmethod
    def setUp(self):
        self.intf = PIControllerInterface()
        self.freshState = PIConfiguration(
            SN=1,
            model=PIControllerModel.mock,
            connection_type=PIConnectionType.usb
        )


    async def test_basic(self):
        assert self.intf.stageInfo == {}

        await self.intf.settings.configurationChangeRequest(self.freshState)
        assert len(self.intf.settings.currentConfiguration) == 1
        assert self.intf.settings.currentConfiguration[0].connection_type == PIConnectionType.usb

    async def test_add_configuration(self):
        state = self.freshState
        state.channel_amount = 4
        state.stages = ["NOSTAGE"] * 4
        await self.intf.settings.configurationChangeRequest(state)
        assert self.intf.settings.currentConfiguration[0].channel_amount == 4
        assert self.intf.settings.currentConfiguration[0].stages == state.stages
        print("weewewwe")

