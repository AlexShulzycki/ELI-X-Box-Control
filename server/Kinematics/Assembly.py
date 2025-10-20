from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field

from scipy.spatial.transform import Rotation as R

from server.Interface import toplevelinterface
from server.Kinematics.DataTypes import XYZvector, ComponentType
from server.Devices.DataTypes import StageStatus
from server.utils.EventAnnouncer import EventAnnouncer


class CollisionBox(BaseModel):
    BoxDimensions: XYZvector = Field(default= XYZvector(), description="Box dimensions")
    BoxOffset: XYZvector = Field(default= XYZvector(), description="location of center of box")

    class Config:
        arbitrary_types_allowed = True


class AttachmentPoint(BaseModel):
    Point: XYZvector = Field(default= XYZvector(), description="Position of the attached comp relative to the parent's root position")
    Rotation: R = Field(description="Rotation object translating world-space to component-space", default=R.from_quat([0, 0, 0, 1]))
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

        rotation = self.root.Rotation
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

    @property
    def JSON(self) -> dict:
        """
        Describes this object and its children in a dict
        :return: json-ready dict
        """

        children = []
        for child in self.attachments:
            children.append(child.JSON)

        res = {
            "name": self.name,
            "type": ComponentType.Component,
            "children": children,
            "attachment_point": [0,0,0],
            "attachment_rotation": [0,0,0,1]
        }
        if self.root is not None:
            res["attachment_point"] = self.root.Point.xyz
            res["attachment_rotation"] = list(self.root.Rotation.as_quat())

        return res

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

    @property
    def JSON(self) -> dict:
        res = super().JSON
        res["collision_box_dimensions"] = self.collision_box.BoxDimensions.xyz
        res["collision_box_point"] = self.collision_box.BoxOffset.xyz
        res["type"] = ComponentType.Structure

        return res


class AxisComponent(Structure):
    def __init__(self, axisdirection: XYZvector | R, axis_identifier: int, root, name: str = "unnamed axis", collisionbox = None):
        """
        Axis component. Its position is the position of the axis in space.
        :param axis: Axis object that holds a reference to the physical stages
        :param axisdirection: Unit vector pointing to where the axis moves when you increase its position
        :param root: Attachment point -> This always points to the axis zero!
        :param collisionbox: Collision box, this is on the moving axis!
        """
        super().__init__(root, name, collisionbox)
        self.axis_identifier: int = axis_identifier
        self.axis_vector: XYZvector | R = axisdirection
        """Vector pointing to where the axis moves when you increase its position by 1"""

    def getXYZ(self, currentXYZ: XYZvector = XYZvector()) -> XYZvector:
        """
        Override parent method, update the attachment position as the real axis moves
        :return:
        """
        # Move vector to where the axis is right now
        try:
            ax_pos = toplevelinterface.StageStatus.get(self.axis_identifier)
        except KeyError as e:
            raise Exception(f"Could not find axis {self.axis_identifier} in the toplevelinterface")

        if type(self.axis_vector) == XYZvector:
            displacement_vector = XYZvector((self.axis_vector * ax_pos).xyz)
            currentXYZ += displacement_vector
        elif type(self.axis_vector) == R:
            currentXYZ = self.axis_vector.apply(currentXYZ.xyz)

        # Continue calculations
        return super().getXYZ(currentXYZ)

    @property
    def JSON(self) -> dict:
        res = super().JSON

        # handle the axis vector for linear, rotational, and other stages
        if type(self.axis_vector) == XYZvector:
            res["axis_vector"] = self.axis_vector.xyz
        elif type(self.axis_vector) == R:
            res["axis_vector"] = list(self.axis_vector.as_quat())
        else:
            res["axis_vector"] = None

        res["axis_identifier"] = self.axis_identifier
        res["type"] = ComponentType.Axis
        return res



# Set up the main interface
class AssemblyInterface:
    def __init__(self):
        self.EA = EventAnnouncer(AssemblyInterface, StageStatus)
        self._root: Component = Component(name="root") # For now we create a root, rethink this

    @property
    def root(self):
        return self._root

    @root.setter
    def root(self, component: Component):
        if component.name !="root":
            raise Exception("Root component needs to be called root")
        self._root = component
        print("Root has been replaced!")


    def traverseTree(self, name:str, root = None) -> Component|None:
        """Return a component with the given name"""
        if root is None:
            root = self.root
        # check if root
        if root.name == name:
            return root
        # traverse the treee
        for childcomponent in root.attachments:
            # check if this is it
            if childcomponent.name == name:
                return childcomponent
            # if not, check its children
            else:
                traverse_child = self.traverseTree(name, childcomponent)
                if traverse_child is not None:
                    # if we found it, return
                    return traverse_child

        # if we got all the way here we found nothing
        return None

    def attach(self, comp: Component, attachment: AttachmentPoint):
        # Check for name duplicates
        if self.traverseTree(comp.name, self.root) is not None:
            # Already exists
            raise Exception(f"Already have a component with the name {comp.name}, pick a different one")

        # Try to find the component we want to attach to
        if self.traverseTree(attachment.Attached_To_Component.name, self.root) is None:
            # Cant find target
            raise Exception(f"Cannot find component with name {attachment.Attached_To_Component.name}")
        else:
            comp.attach(attachment)


    def unattach(self, targetname: str):
        traverse = self.traverseTree(targetname, self.root)
        if traverse is None:
            # cant find it
            raise Exception(f"No component with name {targetname} found")
        else:
            traverse.unattach()

    def getJson(self) -> dict:
        """
        Describe the entire thing in JSON-ready dict
        :return: what do you think
        """
        return self.root.JSON