from pydantic import BaseModel, Field
from typing import Annotated


class Axis(BaseModel):
    name: str
    # enum type linear/rotation etc
    # collision box
    collisionBox: list[Annotated[int, Field(description="dimension of a side of the box",
                                            examples=[10, 0, 3],
                                            ge=0)]] = Field(
        description="Dimensions of the collision box, in XYZ lengths, centered on the moving axis position",
        min_length=3, max_length=3, examples=[[10, 20, 0]], default=[0, 0, 0], validate_default=True)


class AssemblySchema(BaseModel):
    name: str


# create a box around the moving part


class Assembly():
    def __init__(self):
        # validate schema, validate axes
        raise NotImplemented
