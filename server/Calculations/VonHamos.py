import math
from enum import Enum

from pydantic import BaseModel, Field
from decimal import Decimal, ROUND_HALF_UP


class Triangle:
    """
    Instance of a calculated Von Hamos triangle.
    """

    def __init__(self, n: int, a: Decimal, c: Decimal, theta: Decimal, type: str, energy: float, crystal: str = None,
                 elementline: str = None):
        """
        New Triangle object
        @param n: N order of the triangle
        @param a: Length from the source/sample to the crystal
        @param c: Hypotenuse
        @param theta: Angle in the corner of the sample/source
        @param type: "XES" or "XAS"
        @param energy: Energy to be used in eV
        @param crystal: Label for the crystal used in this triangle
        @param elementline: Label for the element used in this triangle
        """
        self.n = n
        self.a = a
        self.c = c
        self.theta = theta
        self.type = type
        self.energy = energy
        self.crystal = crystal
        self.elementline = elementline


def validValue(value):
    """
    Checks if the input is valid, i.e. a positive float. If not, raises exception
    @param value: The input to be checked
    @type value: str
    @return: The input, in float form
    @rtype: float
    """
    # input = re.sub(r',', '.', input) # for replacing commas with periods, we assume our users don't use them for now
    return float(value)


def buildVonHamos(energy: str, latticeConstant: str, n_order: int, type: str, crystal: str = None,
                  elementline: str = None) -> list[Triangle]:
    """
    Calculates series of triangles of n-th order. The calculation is based on Braggs law
    and Von Hamos triangle with constant distance between crystal and sensor (25cm). Input raw strings, throws
    exceptions on bad inputs. All units in centimeters and degrees.

    Returns a list of values in the form: [n, a, c, angle]. Raises exception on bad inputs
    -------
    @param energy: Emission line
    @param latticeConstant: Lattice constant of the crystal
    @param n_order: How many orders to calculate
    @param type: XAS or XES
    @param crystal: Name of the crystal, i.e. Si111
    @param elementline: Name of the energy line, i.e. Ka1
    @return: VonHamos.Triangle object
    """
    # Check the inputs first
    energy = validValue(energy)
    latticeConstant = validValue(latticeConstant)

    # If we made it here, we're all good, lets continue

    triangles = []  # Calculated triangles

    e = float(energy)  # from string to float
    lam = 1.24e-6 / e  # 1.24e-6" constant -> lambda = E/(h*c)*unit_crystal_conversion

    for j in range(n_order):
        # Braggs law gives us angle = arcsin(n*lambda/2*LATTICE_CONSTNAT)
        # + conversion from unit cell to lattice constant (thus the "10^10")

        # TODO Verify equation
        sinTheta = (j + 1) * lam * 1e10 / latticeConstant
        if abs(sinTheta) <= 1:  # otherwise asin doesn't make sense
            theta = math.asin(sinTheta)
            theta = theta * 180 / math.pi  # converts radians to degrees

            if theta < 5:
                # too small to care about
                continue
        else:
            # Not possible, add an empty triangle and exit. Increasing the
            # order makes no sense, because the sin theta is already
            # above 1, multiplying with a bigger order will only make it bigger.
            # TODO indicate there is no valid reflection
            triangles.append(None)
            break

        # isosceles triangle yields equations for the "a" and "c" sides:
        x = 25  # 25cm is constant distance between sensor and crystal
        a = x / sinTheta
        c = 2 * math.sqrt(a ** 2 - 25 ** 2)  # pythagorian theorem a^2 - 25^2 = c^2/2

        # rounding up results
        a = Decimal(a).quantize(Decimal('0.001'), rounding=ROUND_HALF_UP)
        c = Decimal(c).quantize(Decimal('0.001'), rounding=ROUND_HALF_UP)
        theta = Decimal(theta).quantize(Decimal('0.001'), rounding=ROUND_HALF_UP)

        # [n, a, c, angle]
        triangles.append(Triangle(j + 1, a, c, theta, type, e, crystal, elementline))  # list of lists
    return triangles


def getElementEnergies(data, element) -> dict[str, float]:
    """
    Gets the energies of an element and returns in a 2d dict
    @param data: XES or XAS data
    @param element: Chemical element, i.e. Fe
    @return: data[element], to get labels you do .keys(), similarly .values()
    """
    try:
        return data[element]
    except KeyError as e:
        print("Cannot retrieve element: " + e.__str__())


def getElementLatticeDict(drumConfig: dict) -> dict[str, float]:
    """
    Gets dict of crystal element names and lattice constants. Retrieve names, lattice constant by .keys() and .values()
    @param drumConfig: Drumconfig dict
    @return: {Name:LatticeConstant}
    """
    output = {}
    for drumSettings in drumConfig.keys():
        currentDrum = drumConfig[drumSettings]
        for sideSettings in ["0", "1", "2", "3"]:
            side = currentDrum[sideSettings]
            # Check if name is empty, only add to list if not empty
            if side["Name"] != "Empty" and side["Name"] != "":
                # Otherwise, we are in business
                output[side["Name"]] = float(side["LatticeConstant"])
    return output


