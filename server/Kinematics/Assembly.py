from pydantic import BaseModel, Field
from typing import Annotated
from server.StageControl.DataTypes import StageKind, StageInfo


class Axis(BaseModel):
    # name and type of axis
    name: str
    kind: StageKind | None

    # Physical dimensions and characteristics
    # root
    root: list[Annotated[float, Field(description="Where the root of the stage is located, i.e. stage zero position in xyz space",
                                      examples=[[0,20, -4]], default=[0,0,0], validate_default=True)]]

    # collision box
    collisionBox: list[Annotated[int, Field(description="xyz dimensions for collision box",
                                            examples=[10, 0, 3],
                                            ge=0)]] = Field(
        description="Dimensions of the collision box, in XYZ lengths, centered on the moving axis position",
        min_length=3, max_length=3, examples=[[10, 20, 0]], default=[0, 0, 0], validate_default=True)


class AssemblySchema(BaseModel):
    name: str
    axes: list[Axis]


class Assembly:
    def __init__(self, assemblyschema: AssemblySchema, root = None):
        # validate schema, validate axes
        self.schema = assemblyschema
        self.root:Assembly = root
        raise NotImplemented
