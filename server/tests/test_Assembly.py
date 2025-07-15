from unittest import TestCase

import numpy as np
import scipy.constants

from server.Kinematics.Assembly import Component, AttachmentPoint, XYZvector


class TestAssembly(TestCase):
    pass


class TestComponent(TestCase):
    @classmethod
    def setUpClass(self):
        self.component1 = Component()
        self.component2 = Component()
        self.component3 = Component()

        self.component2.attach(AttachmentPoint(
            Point= XYZvector([0,1,0]),
            Attached_To_Component=self.component1
        ))

        self.component3.attach(AttachmentPoint(
            Point= XYZvector([1,0,1]),
            Attached_To_Component=self.component2
        ))

    def test_get_xyz(self):
        xyz = self.component3.getXYZ()
        assert xyz.xyz == [1,1,1]

    def test_rotate(self):
        self.component4 = Component()
        self.component4.attach(AttachmentPoint(
            Point= XYZvector([0,1,0]),
            Attached_To_Component=self.component3
        ))
        self.component3.root.RotationVector = XYZvector([0,0,scipy.constants.pi])
        xyz = self.component4.getXYZ()
        print(np.round(xyz.xyz))
        assert list(np.round(xyz.xyz)) == [1,0,1]

    def test_delete(self):
        print(self.component2.attachments)
        self.component3.unattach()
        print(self.component2.attachments)

        assert self.component3.attachments == []
