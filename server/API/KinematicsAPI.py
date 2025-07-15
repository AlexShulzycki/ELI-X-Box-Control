from fastapi import APIRouter, HTTPException
from server.Kinematics.Assembly import Axis

router = APIRouter(tags=["control"])

@router.get("/kinematics/assemblies")
async def getassemblies() -> list[StageInfo]:
    """
    Get configured assemblies
    """
    return await res