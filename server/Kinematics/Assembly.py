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
    def __init__(self, root=None, collisionbox: CollisionBox = None):
        """
        Structure component, has a collision box. Doesn't do anything right now.
        :param root: what it's attached to
        :param collisionbox: Collision box
        """
        super().__init__(root)

        self.collision_box = collisionbox
        if self.collision_box is None:
            self.collision_box = CollisionBox()


class AxisComponent(Structure):
    def __init__(self, axisdirection: XYZvector, axis: Axis, root, collisionbox = None):
        """
        Axis component. Its position is the position of the axis in space.
        :param axis: Axis object that holds a reference to the physical stages
        :param axisdirection: Unit vector pointing to where the axis moves when you increase its position
        :param root: Attachment point -> This always points to the axis zero!
        :param collisionbox: Collision box, this is on the moving axis!
        """
        super().__init__(root, collisionbox)
        self.axis: Axis = axis
        self.axis_vector: XYZvector = axisdirection

        # For the axis component, we need to update the attachment positon as the real axis moves
        @Component.root.getter
        def root(self) -> AttachmentPoint:
            print("GETTER")
            value = super().root
            zero_point = value.Point
            ax_pos = self.axis.getStatus().position
            displacement_vector = self.axis_vector.xyz * ax_pos
            point = zero_point + displacement_vector

            # make a copy of the current root to modify so we don't lose the zero point
            result = value.__copy__()
            result.Point = point
            return result

        @root.setter
        def root(self, root: AttachmentPoint):
            # Simple setter, replace the whole thing
            self._root = root
