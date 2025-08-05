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

class MoveStageRequest(BaseModel):
    identifier: int = Field(description="The stage identifier of the stage you want to move")
    position: float = Field(description="The position to which you want to move")

class MoveStageResponse(BaseModel):
    success: bool = Field(description="Whether the stage successfully received the move command")
    error: str = Field(description="The error message in case of failure", default=None)

@router.post("/post/stage/move/")
async def moveStage(request: MoveStageRequest) -> MoveStageResponse:
    """
    Moves the indicated stage
    :param request: Request
    :return: Response
    """
    try:
        await toplevelinterface.moveStage(request.identifier, request.position)
        return MoveStageResponse(success=True)
    except Exception as error:
        return MoveStageResponse(success=False, error=str(error))

class StepStageRequest(BaseModel):
    identifier: int = Field(description="The stage identifier of the stage you want to step")
    step: float = Field(description="amount by which you want to move (negative for going the other way)")

@router.post("/get/stage/step/")
async def stepStage(request: StepStageRequest) -> MoveStageResponse:
    pass