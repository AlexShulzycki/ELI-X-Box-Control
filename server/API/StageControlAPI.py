from collections.abc import Awaitable

from fastapi import APIRouter, HTTPException
from server.Interface import toplevelinterface
from server.StageControl.DataTypes import StageInfo

router = APIRouter(tags=["control"])

@router.get("/stage/allstageinfo")
async def getAllStageInfo() -> list[StageInfo]:
    """
    Gets the status of connected stages
    """
    res: Awaitable[list[StageInfo]] = toplevelinterface.getAllStages()
    return await res


# TBD if we need a post request to do multiple
@router.get("/stage/stageinfo/{identifier}")
async def getStageInfoByIdentifier(identifier: int) -> StageInfo:
    return await toplevelinterface.stageInfo([identifier])