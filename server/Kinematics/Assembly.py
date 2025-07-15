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
    BoxDimensions: XYZvector
    BoxOffset: XYZvector

    class Config:
        arbitrary_types_allowed = True


class ComponentType(Enum):
    Structure = "Structure"
    Axis = "Axis"
    Payload = "Payload"

class AttachmentPoint(BaseModel):
    Point: XYZvector
    RotationVector: XYZvector = Field(description="Rotation vector. "
                                                  "[0,0,pi] is a clockwise 180 degree rotation about the z axis",
                                      default=XYZvector([0,0,0]))
    Attached_To_Component: Component = Field(description="Component this attaches to")

    class Config:
        arbitrary_types_allowed = True

class Component:
    def __init__(self, root: AttachmentPoint = None):
        """
        Component base class
        :param root: What this component is attached to
        """
        self.attachments: list[Component] = []
        self.root = None
        if root is not None:
            self.attach(root)

    def attach(self, attachment_point: AttachmentPoint):
        """
        Attach this component via this attachment point
        :param attachment_point: Attachment point object
        """
        if self.root is not None:
            # Double check if we are already not attached to something
            self.unattach()
        else:
            # Set root to the attachment point, and let the root component know
            self.root = attachment_point
            self.root.Attached_To_Component.attachments.append(self)

    def unattach(self):
        if self.root is not None:
            self.root.Attached_To_Component.attachments.remove(self)
            self.root = None

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def getXYZ(self) -> XYZvector:
        """
        Travel up the tree until root is none, calculating its position at each step
        """
        currentXYZ = XYZvector()
        root = self.root
        """A bit confusing, root refers to the AttachmentPoint object"""
        while root is not None:
            rotation = Rotation.from_rotvec(root.RotationVector.xyz)
            currentXYZ = XYZvector(rotation.apply(currentXYZ.xyz))
            currentXYZ += root.Point
            # We now get the next attachment point object, via our attachment point, getting the
            # parent component, and then the component's attachment point
            root = root.Attached_To_Component.root

        return currentXYZ

    def __del__(self):
        self.unattach()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.unattach()

class Structure(Component):
    def __init__(self, root=None):
        """
        Structure component, can attach stuff to it and be attached to stuff
        :param root: what it's attached to
        :param attached: what's attached to it
        """
        super().__init__(root)


class AxisComponent(Component):
    def __init__(self, axiszero: XYZvector, axisdirection: XYZvector, axis: Axis, root):
        """
        Axis component
        :param axiszero: Where the axis zero position is relative to the attachment point
        :param axis: Axis object that holds a reference to the physical stages
        :param axisdirection: Unit vector pointing to where the axis moves when you increase its position
        :param root:
        :param attached:
        """
        super().__init__(root, attached)
        self.axis: Axis = axis
        self.axiszero: XYZvector = axiszero
        self.axisdirection: XYZvector = axisdirection
