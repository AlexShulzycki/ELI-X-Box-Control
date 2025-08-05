from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, model_validator

from server.Interface import toplevelinterface
from server.StageControl.DataTypes import StageInfo, StageStatus, StageKind

router = APIRouter(tags=["control"])

@router.get("/get/stage/info")
def getAllStageInfo() -> dict[int, StageInfo]:
    """
    Gets the stage info of connected stages
    :return: dict identifier -> StageInfo
    """
    return toplevelinterface.StageInfo

@router.get("/get/stage/status")
def getAllStageStatus() -> dict[int, StageStatus]:
    """
    Gets the status of connected stages
    :return: dict identifier -> StageStatus
    """
    return toplevelinterface.StageStatus

@router.get("/get/stage/update/status/")
async def updateStageStatus():
    """
    Updates the status of all connected stages
    """
    await toplevelinterface.updateStageStatus()

@router.get("/get/stage/update/info/")
async def updateStageInfo():
    """
    Updates the info of all connected stages
    """
    await toplevelinterface.updateStageInfo()

class FullState(BaseModel):
    identifier: int
    model: str
    kind: StageKind
    minimum: float
    maximum: float
    connected: bool
    ready: bool
    position: int
    ontarget: bool


@router.get("/get/stage/fullstate")
async def getStageFullstate():
    info = toplevelinterface.StageInfo
    stat = toplevelinterface.StageStatus
    res: dict[int, FullState] = {}
    for key in info.keys():
        res[key] = FullState(
            identifier=info[key].identifier,
            model=info[key].model,
            kind=info[key].kind,
            minimum=info[key].minimum,
            maximum=info[key].maximum,
            connected=stat[key].connected,
            ready=stat[key].ready,
            position=stat[key].position,
            ontarget=stat[key].ontarget,
        )
    return res

class MoveStageResponse(BaseModel):
    success: bool = Field(description="Whether the stage successfully received the move command")
    error: str = Field(description="The error message in case of failure", default=None)

@router.get("/get/stage/move/")
async def moveStage(identifier: int, position: int) -> MoveStageResponse:
    """
    Moves the indicated stage
    :param request: Request
    :return: Response
    """
    try:
        await toplevelinterface.moveStage(identifier, position)
        return MoveStageResponse(success=True)
    except Exception as error:
        return MoveStageResponse(success=False, error=str(error))

@router.get("/get/stage/step/")
async def stepStage(identifier: int, step:int) -> MoveStageResponse:
    try:
        await toplevelinterface.stepStage(identifier, step)
        return MoveStageResponse(success=True)
    except Exception as error:
        return MoveStageResponse(success=False, error=str(error))