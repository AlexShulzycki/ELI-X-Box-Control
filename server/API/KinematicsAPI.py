from fastapi import APIRouter, HTTPException
from server.Interface import toplevelAssemblyInterface

router = APIRouter(tags=["control"])

@router.get("/kinematics/assemblies")
async def getassemblies():
    """
    Get configured assemblies
    """
    pass

@router.get("/kinematics/assembly")