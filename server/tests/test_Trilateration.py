from unittest import TestCase

from server.Kinematics.DataTypes import XYZvector
from server.Kinematics.Trilateration import Trilateration, trilaterate


class TestTrilateration(TestCase):

    @staticmethod
    def basic_trilat():
        tri = Trilateration()
        tri.addMeasurement(XYZvector([0, 0, 0]), 1)
        tri.addMeasurement(XYZvector([0, 2, 0]), 1)
        tri.addMeasurement(XYZvector([0, 1, 1]), 1)
        tri.addMeasurement(XYZvector([1, 1, 0]), 1)
        return tri

    def test_calculate(self):
        # actual point: 0, 1, 0
        tri = Trilateration()
        tri.addMeasurement(XYZvector([0, 0, 0]), 1)
        tri.addMeasurement(XYZvector([0, 2, 0]), 1)
        tri.addMeasurement(XYZvector([0, 1, 1]), 1)
        tri.addMeasurement(XYZvector([0, 1, -1]), 1)

        res = trilaterate(tri.measurements)
        print(res)
        assert res == XYZvector([0,1,0])

    def test_estimate(self):
        tri = self.basic_trilat()

        assert len(tri.estimates) == 1
        assert tri.estimates[0] == XYZvector([0, 1, 0])

    def test_2_estimates(self):
        tri = self.basic_trilat()
        tri.addMeasurement(XYZvector([0, 3, 0]), 2)
        assert len(tri.estimates) == 5

        for est in tri.estimates:
            x, y, z = est.xyz
            assert round(x) == 0
            assert round(y) == 1
            assert round(z) == 0

    def test_invalid_distance(self):
        tri = self.basic_trilat()
        with self.assertRaises(Exception):
            tri.addMeasurement(XYZvector([0, 5, 0]), 0)
        with self.assertRaises(Exception):
            tri.addMeasurement(XYZvector([0, 5, 0]), -0.6)

    def test_duplicate(self):
        tri = self.basic_trilat()
        with self.assertRaises(Exception):
            tri.addMeasurement(XYZvector([0, 0, 0]), 5)

    def test_negative(self):
        tri = self.basic_trilat()
        tri.addMeasurement(XYZvector([0, -2, 0]), 3)
        for est in tri.estimates:
            x, y, z = est.xyz
            assert round(x) == 0
            assert round(y) == 1
            assert round(z) == 0

    def test_errors(self):
        tri = Trilateration()
        tri.addMeasurement(XYZvector([0, 0, 0]), 1)
        tri.addMeasurement(XYZvector([0, 2, 0]), 1)
        tri.addMeasurement(XYZvector([0, 1, 1]), 1)
        tri.addMeasurement(XYZvector([1, 1, 0]), 1)
        tri.addMeasurement(XYZvector([2, 1, 0]), 2)
        tri.addMeasurement(XYZvector([-3, 1, 0]), 3)
        print(tri.average)
        print(tri.std)