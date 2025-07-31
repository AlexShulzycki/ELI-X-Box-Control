import os
from unittest import TestCase
os.chdir("../") # move to main server directory instead of /tests
print(os.getcwd())
from server.Calculations.VonHamos import Alignment, Triangle
from server.Calculations.DataTypes import elements, crystals


class TestAlignment(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        pass

    def test_theta_absorption(self):
        alignment = Alignment(
            element=elements["Fe"],
            crystal=crystals[0],
        )

        print(alignment.model_dump())
        triangle = Triangle(alignment=alignment, max_a= 500, max_c= 500)

        print(triangle.model_dump())

    #def test_theta_emission(self):
        #self.fail()

    #def test_calculate_theta(self):
        #self.fail()
