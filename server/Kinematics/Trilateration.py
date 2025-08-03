import numpy as np
from itertools import combinations

from server.Kinematics.DataTypes import XYZvector

class Trilateration:

    def __init__(self, margin_of_error: float = 2):
        """
        Start a new trilateration
        :param margin_of_error: expected margin of error for distance measurements, in mm.
        """
        self._measurements: list[tuple[XYZvector, float]] = []
        self._estimates: list[XYZvector] = []

    def addMeasurement(self, point: XYZvector, distance: float):
        """
        Add a distance measurement from a known point to the calculation.
        :param point: Point the distance was measured from
        :param distance: Distance, in mm
        """
        # Check if this measurement already exists and if measurment is bigger than zero
        for measurement in self._measurements:
            if measurement[0] == point:
                raise Exception('Point already measured')
            if distance <= 0.0:
                raise Exception('Distance cannot be zero or negative')

        self._measurements.append((point, distance))

        # recalculate estimates if we have 4 or more measurements
        self.recalculate_estimates()

    @staticmethod
    def calculate(measurements: list[tuple[XYZvector, float]]):
        """
        Given the measurements, calculate an estimate of the position.
        Adapted from https://github.com/akshayb6/trilateration-in-3d/tree/
        Distance cannot be zero, and each point must be different
        :return: Trilaterated XYZVector
        """
        # points we measured from
        p1 = np.array(measurements[0][0].xyz)
        p2 = np.array(measurements[1][0].xyz)
        p3 = np.array(measurements[2][0].xyz)
        p4 = np.array(measurements[3][0].xyz)
        # distances from each point
        r1 = measurements[0][1]
        r2 = measurements[1][1]
        r3 = measurements[2][1]
        r4 = measurements[3][1]
        # calculations from https://github.com/akshayb6/trilateration-in-3d/tree/
        e_x = (p2 - p1) / np.linalg.norm(p2 - p1)
        i = np.dot(e_x, (p3 - p1))
        e_y = (p3 - p1 - (i * e_x)) / (np.linalg.norm(p3 - p1 - (i * e_x)))
        e_z = np.cross(e_x, e_y)
        d = np.linalg.norm(p2 - p1)
        j = np.dot(e_y, (p3 - p1))
        x = ((r1 ** 2) - (r2 ** 2) + (d ** 2)) / (2 * d)
        y = (((r1 ** 2) - (r3 ** 2) + (i ** 2) + (j ** 2)) / (2 * j)) - ((i / j) * (x))
        z1 = np.sqrt(r1 ** 2 - x ** 2 - y ** 2)
        z2 = np.sqrt(r1 ** 2 - x ** 2 - y ** 2) * (-1)
        ans1 = p1 + (x * e_x) + (y * e_y) + (z1 * e_z)
        ans2 = p1 + (x * e_x) + (y * e_y) + (z2 * e_z)
        dist1:float = float(np.linalg.norm(p4 - ans1))
        dist2:float = float(np.linalg.norm(p4 - ans2))
        if np.abs(r4 - dist1) < np.abs(r4 - dist2):
            return XYZvector(ans1)
        else:
            return XYZvector(ans2)

    @property
    def measurements(self) -> list[tuple[XYZvector, float]]:
        return self._measurements

    @property
    def estimates(self) -> list[XYZvector]:
        return self._estimates


    def recalculate_estimates(self) -> list[XYZvector]:
        """
        If more than 4 measurements are available, return a list of all possible positions
        :return: list of possible positions
        """
        res: list[XYZvector] = []
        # If we have less than 4 measurements, we cannot do any estimates
        if len(self._measurements) < 4:
            return res

        # get possible combinations
        combs = combinations(self._measurements, 4)

        for comb in combs:
            res.append(self.calculate(comb))

        self._estimates = res


