from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from server.Kinematics.Assembly import AssemblyInterface
from server.Kinematics.DataTypes import XYZvector
from server.Kinematics.Trilateration import Trilateration


router = APIRouter(tags=["control", "kinematics"])

tri: Trilateration = Trilateration()
assembly: AssemblyInterface = AssemblyInterface()

@router.get("/kinematics/assemblies")
async def getassemblies():
    """
    Get configured assemblies
    """
    global assembly
    pass


@router.post("/kinematics/saveassembly")



class TrilaterationRequest(BaseModel):
    restart: bool = Field(default=False, examples=[True, False], description="If you want to restart the trilateration process")
    measurements: list[list] = Field(description="List of measurement(s) you want to add. Format: [([x,y,z], distance), ...]")
    class Config:
        arbitrary_types_allowed = True


@router.post("/trilateration")
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