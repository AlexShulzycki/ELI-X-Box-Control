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
        EA = EventAnnouncer(int, str)
        sub = EA.subscribe(str)
        destination = MagicMock()
        sub.deliverTo(str, destination)

        msg = "skibidi wewooowewewewe"
        EA.event(msg)
        destination.assert_called_with(msg)

        # ensure we can unsubscribe from within both the sub and EA
        sub2 = EA.subscribe(str)
        EA.unsubscribe(sub)
        assert len(EA.subs) == 1
        sub2.unsubscribe()
        assert len(EA.subs) == 0


        # final check
        EA.event("")
        # Should still be the old message
        destination.assert_called_with(msg)


class TestSubscription(TestCase):
    pass
