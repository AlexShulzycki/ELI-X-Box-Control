from unittest import TestCase

from server.StageControl.DataTypes import StageInfo
from server.StageControl.Virtual import VirtualControllerInterface


class TestVirtualControllerInterface(TestCase):

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

        self.vinterface.settings.configurationChangeRequest([config1, config2])

    def test_stages(self):
        assert self.vinterface.stages.__contains__(1)

    def test_move_to(self):
        self.vinterface.moveTo(1, 25)
        # TODO Finish implementing the update simulation
        # make sure that it only updates when we run the update function
        #assert self.vinterface.stageStatus[1].position == 0
        self.vinterface.updateStageStatus()
        assert self.vinterface.stageStatus[1].position == 25

    def test_remove_stage(self):
        self.vinterface.settings.removeConfiguration(1)
        self.vinterface.settings.removeConfiguration(2)
        assert self.vinterface.stages == []
        assert self.vinterface.stageStatus == {}
        assert self.vinterface.stageInfo == {}

    def test_add_duplicate(self):

        failed = False
        try:
            self.vinterface.settings.configurationChangeRequest([StageInfo(
                identifier=1,
                model="virtual, but a duplicate!"
            )])
        except:
            failed = True

        assert failed