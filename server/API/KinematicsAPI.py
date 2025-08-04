from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field, model_validator
from scipy.spatial.transform import Rotation

from server.Kinematics.Assembly import AssemblyInterface, AttachmentPoint, Component, Structure, CollisionBox, \
    AxisComponent
from server.Kinematics.DataTypes import XYZvector, ComponentType
from server.Kinematics.Trilateration import Trilateration


router = APIRouter(tags=["control", "kinematics"])

tri: Trilateration = Trilateration()
assembly: AssemblyInterface = AssemblyInterface()

@router.get("/get/kinematics/assemblies")
async def getassemblies():
    """
    Get configured assemblies
    """
    return assembly.getJson()


class ComponentRequest(BaseModel):
    name: str = Field(description="Unique name for this component")
    type: ComponentType
    attach_to: str = Field(description="Unique name of the component this is attached to.", default="root")
    attachment_point: list[float] = Field(min_length=3, max_length=3, default=[0, 0, 0])
    attachment_rotation: list[float] = Field(min_length=4, max_length=4, default=[0, 0, 0, 1])
    collision_box_dimensions: list[float] = Field(min_length=3, max_length=3, default=[5,2,5])
    collision_box_point: list[float] = Field(min_length=3, max_length=3, default = [0,1,0])
    axis_vector: list[float] = Field(min_length=3, max_length=4, default=None)
    axis_identifier: int = Field(default=None)
    children: list[ComponentRequest] = Field(default=[])

    @model_validator(mode= "after")
    def validate(self):
        if self.type == ComponentType.Axis:
            if self.axis_identifier is None:
                raise ValueError("axis_identifier must be set for axis components")
        return self


@router.post("/post/kinematics/addComponent")
def addcomponent(root: ComponentRequest):
    # We traverse the component tree
    def attach(compreq: ComponentRequest, rootname: str):
        """
        Recursive attacher that converts from request to actual assembly, works with the assembly interface
        :param compreq: component request object
        :param rootname: name of the component this request attaches to (i.e. the parent)
        :return:
        """
        attachmentPoint = AttachmentPoint(
            Attached_To_Component=assembly.traverseTree(rootname),
            Point= XYZvector(compreq.attachment_point),
            Rotation=Rotation.from_quat(compreq.attachment_rotation),
        )
        cbox = CollisionBox(
            BoxDimensions=XYZvector(compreq.collision_box_dimensions),
            BoxOffset=XYZvector(compreq.collision_box_point),
        )

        # Create relevant components (kind of convoluted, I know, but whatever)
        comp: Component|None = None
        if root.type == ComponentType.Component:
            comp = Component(root=attachmentPoint, name=compreq.name)
        elif root.type == ComponentType.Structure:
            comp = Structure(root=attachmentPoint, name=compreq.name, collisionbox=cbox)
        elif root.type == ComponentType.Axis:
            ax_dir = None
            if len(compreq.axis_vector) == 4: # Quaternion
                ax_dir = Rotation.from_quat(compreq.axis_vector)
            elif len(compreq.axis_vector) == 3: # Regular vector
                ax_dir = XYZvector(compreq.axis_vector)

            comp = AxisComponent(root=attachmentPoint, name=compreq.name, collisionbox=cbox,
                             axisdirection=ax_dir, axis_identifier=compreq.axis_identifier)

        # we don't need to attach anything manually, by passing the attachmentPoint to the constructor the
        # component takes care of that automagically

        # recursive fun!
        for child in compreq.children:
            attach(child, compreq.name)

    # Let's kick it all off
    attach(root, root.attach_to)

@router.get("get/kinematics/removeComponent")
def removecomponent(name: str):
    assembly.unattach(name)

@router.post("/post/kinematics/replaceRoot")
def replaceRoot(root: ComponentRequest):
    """Replace the entire assembly"""
    # Let's kick off the recursion
    if root.type != ComponentType.Component:
        raise ValueError("Root component must be a component, not axis or structure etc")
    assembly.root = Component(name="root")
    for child in root.children:
        addcomponent(child)

    return assembly.getJson()

@router.get("/get/kinematics/saveassembly")
def saveassembly():
    raise NotImplementedError()

class TrilaterationRequest(BaseModel):
    restart: bool = Field(default=False, examples=[True, False], description="If you want to restart the trilateration process")
    measurements: list[list] = Field(description="List of measurement(s) you want to add. Format: [([x,y,z], distance), ...]")
    class Config:
        arbitrary_types_allowed = True


@router.post("/post/trilateration")
async def trilaterate(req: TrilaterationRequest):
    """
    {"restart":true,"measurements":[[[0,0,0],1],[[0,2,0],1],[[1,1,0],1],[[-1,1,0],1]]}
    :param req: TrilaterationRequest
    :return:
    """
    global tri
    if req.restart:
        tri = Trilateration()

    for m in req.measurements:
        tri.addMeasurement(XYZvector(m[0]), m[1])

    return {
        "points": len(tri.measurements),
        "estimates": len(tri.estimates),
        "average" : tri.average,
        "std": tri.std,
    }