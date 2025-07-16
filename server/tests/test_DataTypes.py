from unittest import TestCase
from unittest.mock import MagicMock

from server.StageControl.DataTypes import EventAnnouncer


class TestEventAnnouncer(TestCase):

    @classmethod
    def setUpClass(self) -> None:
        pass

    def test_subscribe_deliver_basic(self):
        EA = EventAnnouncer(int, str)

        strfunc = MagicMock()
        intfunc = MagicMock()

        sub = EA.subscribe(str, int)
        sub.deliverTo(int, intfunc)
        sub.deliverTo(str, strfunc)

        EA.event(5)
        EA.event(str("five"))

        strfunc.assert_called_with("five")
        intfunc.assert_called_with(5)

    def test_unsubscribe(self):
        self.fail()


class TestSubscription(TestCase):
    pass
