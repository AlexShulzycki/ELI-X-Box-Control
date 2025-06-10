from pydantic import BaseModel, Field








### Legacy code below

class Geometry:

    def __init__(self, settings, axes):

        # Save the parameters
        self.axes = axes
        self.settings = settings

        # Create empty vars to populate
        self.xesLimits = {}
        self.xasLimits = {}

        # Calculate limits
        self.XESlimits()
        self.XASlimits()


    def XESlimits(self):
        """
        Calculates limits for XES axes and puts them in self.xesLimits
        @return:
        """
        self.xesLimits = {
            "detx": [self.settings["XESdetxoffset"], self.axes["xesdetx"].range()[1] + self.settings["XESdetxoffset"]],
            "cryx": [self.settings["XEScryxoffset"], self.axes["xescryx"].range()[1] + self.settings["XEScryxoffset"]]
        }

    def XASlimits(self):
        """
        Calulates limits for XAS axes and puts them in self.xasLimits
        @return:
        """
        self.xasLimits = {
            "detx": [self.settings["XASdetxoffset"], self.axes["xasdetx"].range()[1] + self.settings["XASdetxoffset"]],
            "dety": [self.settings["XASdetyoffset"], self.axes["xasdety"].range()[1] + self.settings["XASdetyoffset"]],
            "cryy": [self.settings["XAScryyoffset"], self.axes["xascryy"].range()[1] + self.settings["XAScryyoffset"]]
        }

    def inLimits(self, triangle: Triangle) -> bool:
        """
        Checks if the triangle described by the triangle object is in range of the axes
        @param triangle: Triangle object to verify
        @return: Whether its in range or not
        """

        if triangle.type.__eq__("XES"):
            # Check if each axis is in limits
            detx = self.xesLimits["detx"][0] < (triangle.c)*10 < self.xesLimits["detx"][1]
            cryx = self.xesLimits["cryx"][0] < (triangle.c/2)*10 < self.xesLimits["cryx"][1]
            return detx and cryx

        # XES is handled, now let's do XAS, same principle applies
        limits = self.xasLimits # for brevity
        geometry = self.getXASGeometry(triangle)

        inlimits = True # Flag
        for key, range in limits.items():
            inlimits = range[0] < geometry[key] < range[1]

        return inlimits


    def getXASGeometry(self, triangle: Triangle) -> dict:
        """
        Get the "raw" lengths without correction
        @param triangle: Triangle which we want to form
        @return: dict containing detx, dety, dettheta, cryy, crytheta
        """
        if triangle.type.__eq__("XES"):
            raise Exception("XAS Triangle expected, was given XES")

        a = float(triangle.a * 10)
        theta = triangle.theta  # Angle from the triangle object, theta is also the naming convention in the rotation
        # stages for angle, and not necessarily theta from the triangle (confusing, sorry)
        sigma = 180 - 2 * theta  # Angle at the top of the isosceles triangle.
        mirrorsigma = sigma/2 # sigma to use in order to correctly reflect the xrays onto the the detector

        # CALCULATING "RAW" angles and lengths without correction
        # Crystal is straightforward
        cryy = a
        crytheta = -180 + mirrorsigma  # We assume zero degrees is facing up in the +y direction, angle counts from -180

        # Calculate right angle triangle from the crystal, calculate x, y and angle from sigma
        detx = math.sin(math.radians(sigma)) * a
        dety = a - math.cos(math.radians(sigma)) * a  # Since this length is from the crystal to the detector,
        # we subtract from a and get length from src to the detector.
        dettheta = mirrorsigma  # Since opposing angles on parallel lines are equal (or whatever that rule is called)

        # All done, format and return
        return {
            "detx": detx,
            "dety": dety,
            "dettheta": dettheta,
            "cryy": cryy,
            "crytheta": crytheta
        }
