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
    def setUp(self):
        self.component1 = Component(name="comp1")
        self.component2 = Component(name="comp2")
        self.component3 = Component(name="comp3")
        print("setupclass")

        self.component2.attach(AttachmentPoint(
            Point=XYZvector([0, 1, 0]),
            Attached_To_Component=self.component1
        ))

        self.component3.attach(AttachmentPoint(
            Point=XYZvector([1, 0, 1]),
            Attached_To_Component=self.component2
        ))

    def test_attach_unattach(self):
        compA = Component(name="compA")
        compB = Component(name="compB", root = AttachmentPoint(
            Attached_To_Component=compA
        ))
        compC = Component(name="compC", root = AttachmentPoint(
            Attached_To_Component=compB
        ))
        compD = Component(name="compD")
        compD.attach(AttachmentPoint(Attached_To_Component=compC))

        assert compA.attachments.__contains__(compB)
        assert compB.root.Attached_To_Component == compA
        assert compB.attachments.__contains__(compC)
        assert compC.root.Attached_To_Component == compB
        assert compC.attachments.__contains__(compD)
        assert compD.root.Attached_To_Component == compC

    def test_loop(self):

        compA = Component(name="compA")
        compB = Component(name="compB")
        failed = False
        try:
            compA.attach(AttachmentPoint(Attached_To_Component=compB))
            compB.attach(AttachmentPoint(Attached_To_Component=compA))
        except Exception:
            failed = True

        assert failed

    def test_get_xyz(self):
        xyz = self.component3.getXYZ()
        assert xyz.xyz == [1, 1, 1]

    def test_rotate(self):
        self.component4 = Component(name="comp4")
        self.component4.attach(AttachmentPoint(
            Point=XYZvector([0, 1, 0]),
            Attached_To_Component=self.component3
        ))
        self.component3.root.RotationVector = XYZvector([0, 0, scipy.constants.pi])
        xyz = self.component4.getXYZ()
        print(np.round(xyz.xyz))
        assert list(np.round(xyz.xyz)) == [1, 0, 1]

    def test_delete(self):
        self.component3.unattach()
        assert self.component3.attachments == [] and self.component3.root is None


class TestAxisComponent(TestCase):
    @classmethod
    def setUp(self):
        # Create virtual axes
        axconfigs = [
            StageInfo(model="Virtual_1", identifier=1, minimum=0, maximum=10),
            StageInfo(model="Virtual_2", identifier=2, minimum=0, maximum=23.4),
        ]
        vinterface.addStagesbyConfigs(axconfigs)

        # X and Y axes connected to each other
        self.comp1 = Component(name="comp1")
        self.ax1 = AxisComponent(axisdirection=XYZvector([1, 0, 0]), axis=Axis(1), root=AttachmentPoint(
            Point=XYZvector([0, 1, 0]),
            Attached_To_Component=self.comp1
        ),name = "ax1")
        self.ax2 = AxisComponent(axisdirection=XYZvector([0, 1, 0]), axis=Axis(2), root=AttachmentPoint(
            Point=XYZvector([0, 1, 0]),
            Attached_To_Component=self.ax1
        ),name = "ax1")

    def test_zeroXYZ(self):
        # assert position
        loc1 = self.ax1.getXYZ().xyz
        loc2 = self.ax2.getXYZ().xyz
        assert loc1 == [0,1,0]
        print(loc2)
        assert loc2 == [0,2,0]

    async def test_moveAxis(self):
        vinterface.moveTo(1, 3)
        vinterface.moveTo(2, 1)

        # update status for each axis, (remember async!)
        await self.ax1.axis.getUpdatedStatus()
        await self.ax2.axis.getUpdatedStatus()

        # assert position
        loc1 = self.ax1.getXYZ().xyz
        loc2 = self.ax2.getXYZ().xyz
        assert loc1 == [3, 1, 0]
        print(loc2)
        assert loc2 == [3, 3, 0]