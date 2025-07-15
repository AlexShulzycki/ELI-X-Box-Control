from unittest import TestCase

import numpy as np
import scipy.constants
from server.Interface import Virtualinterface as vinterface
from server.Kinematics.Assembly import Component, AttachmentPoint, XYZvector, AxisComponent
from server.StageControl.Axis import Axis
from server.StageControl.DataTypes import StageInfo


class TestAssembly(TestCase):
    pass


class TestComponent(TestCase):
    @classmethod
    def setUpClass(self):
        self.component1 = Component()
        self.component2 = Component()
        self.component3 = Component()

        self.component2.attach(AttachmentPoint(
            Point=XYZvector([0, 1, 0]),
            Attached_To_Component=self.component1
        ))

        self.component3.attach(AttachmentPoint(
            Point=XYZvector([1, 0, 1]),
            Attached_To_Component=self.component2
        ))

    def test_get_xyz(self):
        xyz = self.component3.getXYZ()
        assert xyz.xyz == [1, 1, 1]

    def test_rotate(self):
        self.component4 = Component()
        self.component4.attach(AttachmentPoint(
            Point=XYZvector([0, 1, 0]),
            Attached_To_Component=self.component3
        ))
        self.component3.root.RotationVector = XYZvector([0, 0, scipy.constants.pi])
        xyz = self.component4.getXYZ()
        print(np.round(xyz.xyz))
        assert list(np.round(xyz.xyz)) == [1, 0, 1]

    def test_delete(self):
        print(self.component2.attachments)
        self.component3.unattach()
        print(self.component2.attachments)

        assert self.component3.attachments == []


class TestAxisComponent(TestCase):
    @classmethod
    def setUpClass(self):
        # Create virtual axes
        axconfigs = [
            StageInfo(model="Virtual_1", identifier=1, minimum=0, maximum=10),
            StageInfo(model="Virtual_2", identifier=2, minimum=0, maximum=23.4),
        ]
        vinterface.addStagesbyConfigs(axconfigs)

        # X and Y axes connected to each other
        self.comp1 = Component()
        self.ax1 = AxisComponent(axisdirection=XYZvector([1, 0, 0]), axis=Axis(1), root=AttachmentPoint(
            Point=XYZvector([0, 1, 0]),
            Attached_To_Component=self.comp1
        ))
        self.ax2 = AxisComponent(axisdirection=XYZvector([0, 1, 0]), axis=Axis(2), root=AttachmentPoint(
            Point=XYZvector([0, 1, 0]),
            Attached_To_Component=self.ax1
        ))

    def test_zeroXYZ(self):
        # zero out
        vinterface.moveTo(1, 0)
        vinterface.moveTo(2, 1)
        # assert position
        loc1 = self.ax1.getXYZ().xyz
        loc2 = self.ax2.getXYZ().xyz
        assert loc1 == [0,1,0]
        print(loc2)
        assert loc2 == [0,3,0]