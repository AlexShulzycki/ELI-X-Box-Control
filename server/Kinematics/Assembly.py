from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field

from server.StageControl.Axis import Axis

from scipy.spatial.transform import Rotation

class XYZvector:
    def __init__(self, xyz=None):
        if xyz is None:
            xyz = [0, 0, 0]
        self.x = xyz[0]
        self.y = xyz[1]
        self.z = xyz[2]

    def __add__(self, other: XYZvector):
        return XYZvector([self.x + other.x, self.y + other.y, self.z + other.z])

    @property
    def xyz(self):
        return [self.x, self.y, self.z]

    @xyz.setter
    def xyz(self, xyz: list[float]):
        self.x = xyz[0]
        self.y = xyz[1]
        self.z = xyz[2]


class CollisionBox(BaseModel):
    BoxDimensions: XYZvector = Field(default= XYZvector(), description="Box dimensions")
    BoxOffset: XYZvector = Field(default= XYZvector(), description="location of center of box")

    class Config:
        arbitrary_types_allowed = True


class ComponentType(Enum):
    Structure = "Structure"
    Axis = "Axis"
    Payload = "Payload"

class AttachmentPoint(BaseModel):
    Point: XYZvector = Field(default= XYZvector(), description="Position of the attached comp relative to the parent's root position")
    RotationVector: XYZvector = Field(description="Rotation vector. "
                                                  "[0,0,pi] is a clockwise 180 degree rotation about the z axis",
                                      default=XYZvector([0,0,0]))
    Attached_To_Component: Component = Field(description="Component this attaches to")

    class Config:
        arbitrary_types_allowed = True

class Component:
    def __init__(self, root: AttachmentPoint = None, name: str = "unnamed component"):
        """
        Component base class
        :param root: What this component is attached to
        """
        self.attachments: list[Component] = []
        self.name = name
        self.root = None
        """A bit confusing, root refers to the AttachmentPoint object"""
        if root is not None:
            self.attach(root)

    def attach(self, attachment_point: AttachmentPoint):
        """
        Attach this component via this attachment point
        :param attachment_point: Attachment point object
        """
        #print(f"attaching {self.name} to {attachment_point.Attached_To_Component.name}")
        if self.root is not None:
            # Double check if we are already not attached to something
            self.unattach()
        else:
            # Check that we are not creating a loop
            comp = attachment_point.Attached_To_Component
            for i in range(0,100):
                if comp == self:
                    raise Exception("Attachments loop into each other")
                if comp is None or comp.root is None:
                    # We reached the end
                    break
                comp = comp.root.Attached_To_Component

            # All good, we can attach
            # Set root to the attachment point, and let the root component know
            self.root = attachment_point
            self.root.Attached_To_Component.attachments.append(self)

    def unattach(self):
        if self.root is not None:
            self.root.Attached_To_Component.attachments.remove(self)
            self.root = None

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def getXYZ(self, currentXYZ: XYZvector = XYZvector()) -> XYZvector:
        """
        Travel up the tree until root is none, calculating its position at each step. We receive an XYZvector
        pointing towards our root location (0,0,0) and we transform this in accordance to our attachment point so that
        it points towards our parent's root location (0,0,0)
        :param currentXYZ: Child node XYZ attachment point relative to our root
        """

        # Check if this is the final component
        if self.root is None:
            return currentXYZ

        # Otherwise calculate

        rotation = Rotation.from_rotvec(self.root.RotationVector.xyz)
        currentXYZ = XYZvector(rotation.apply(currentXYZ.xyz))
        currentXYZ += self.root.Point

        # Call the root attachment's component to continue the calculation
        return self.root.Attached_To_Component.getXYZ(currentXYZ)


    # getter and setter for root
    @property
    def root(self):
        return self._root
    @root.setter
    def root(self, root: AttachmentPoint):
        self._root = root

    def __del__(self):
        self.unattach()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.unattach()

class Structure(Component):
    def __init__(self, root=None, name:str="unnamed structure", collisionbox: CollisionBox = None):
        """
        Structure component, has a collision box. Doesn't do anything right now.
        :param root: what it's attached to
        :param collisionbox: Collision box
        """
        super().__init__(root, name)

        self.collision_box = collisionbox
        if self.collision_box is None:
            self.collision_box = CollisionBox()


class AxisComponent(Structure):
    def __init__(self, axisdirection: XYZvector, axis: Axis, root, name: str = "unnamed axis", collisionbox = None):
        """
        Axis component. Its position is the position of the axis in space.
        :param axis: Axis object that holds a reference to the physical stages
        :param axisdirection: Unit vector pointing to where the axis moves when you increase its position
        :param root: Attachment point -> This always points to the axis zero!
        :param collisionbox: Collision box, this is on the moving axis!
        """
        super().__init__(root, name, collisionbox)
        self.axis: Axis = axis
        self.axis_vector: XYZvector = axisdirection
        """Vector pointing to where the axis moves when you increase its position by 1"""

    def getXYZ(self, currentXYZ: XYZvector = XYZvector()) -> XYZvector:
        """
        Override parent method, update the attachment position as the real axis moves
        :return:
        """
        # Move vector to where the axis is right now
        ax_pos = self.axis.getStatus().position
        displacement_vector = XYZvector(self.axis_vector.xyz * ax_pos)
        currentXYZ += displacement_vector

        # Continue calculations
        return super().getXYZ(currentXYZ)

