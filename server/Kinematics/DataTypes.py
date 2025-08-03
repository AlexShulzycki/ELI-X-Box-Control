from __future__ import annotations


class XYZvector:
    def __init__(self, xyz=None):
        if xyz is None:
            xyz = [0, 0, 0]
        self.x = float(xyz[0])
        self.y = float(xyz[1])
        self.z = float(xyz[2])

    def __add__(self, other: XYZvector):
        return XYZvector([self.x + other.x, self.y + other.y, self.z + other.z])

    def __mul__(self, other: float):
        return XYZvector([self.x * other, self.y * other, self.z * other])

    def __eq__(self, other: XYZvector):
        return self.x == other.x and self.y == other.y and self.z == other.z

    def __str__(self):
        return f"({self.x}, {self.y}, {self.z})"

    @property
    def xyz(self):
        return [self.x, self.y, self.z]

    @xyz.setter
    def xyz(self, xyz: list[float]):
        self.x = xyz[0]
        self.y = xyz[1]
        self.z = xyz[2]
