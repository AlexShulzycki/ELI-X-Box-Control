from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from server.Kinematics.DataTypes import XYZvector
from server.Kinematics.Trilateration import Trilateration

router = APIRouter(tags=["control"])

tri: Trilateration = Trilateration()

@router.get("/kinematics/assemblies")
async def getassemblies():
    """
    Get configured assemblies
    """
    pass

class TrilaterationRequest(BaseModel):
    restart: bool = Field(default=False, examples=[True, False], description="If you want to restart the trilateration process")
    measurements: list[tuple[XYZvector, float]] = Field(description="List of measurement(s) you want to add")


@router.post("/trilateration")
async def trilaterate(req: TrilaterationRequest):
    global tri
    if req.restart:
        tri = Trilateration()

    for m in req.measurements:
        tri.addMeasurement(m[0], m[1])

    return {
        "points": len(tri.measurements),
        "estimates": len(tri.estimates),
        "average" : tri.average,
        "std": tri.std,
    }