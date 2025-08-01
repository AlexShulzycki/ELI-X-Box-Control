from fastapi import APIRouter, HTTPException

router = APIRouter(tags=["control"])

@router.get("/kinematics/assemblies")
async def getassemblies():
    """
    Get configured assemblies
    """
    pass
