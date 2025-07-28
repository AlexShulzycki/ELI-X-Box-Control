from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, model_validator

from server.Interface import toplevelinterface
from server.StageControl.DataTypes import StageInfo, StageStatus

router = APIRouter(tags=["control"])

@router.get("/stage/info")
def getAllStageInfo() -> dict[int, StageInfo]:
    """
    Gets the stage info of connected stages
    :return: dict identifier -> StageInfo
    """
    return toplevelinterface.StageInfo

@router.get("/stage/status")
def getAllStageStatus() -> dict[int, StageStatus]:
    """
    Gets the status of connected stages
    :return: dict identifier -> StageStatus
    """
    return toplevelinterface.StageStatus

@router.get("/stage/update/status/")
async def updateStageStatus():
    """
    Updates the status of all connected stages
    """
    toplevelinterface.updateStageStatus()

@router.get("/stage/update/info/")
async def updateStageInfo():
    """
    Updates the info of all connected stages
    """
    toplevelinterface.updateStageInfo()

class MoveStageRequest(BaseModel):
    identifier: int = Field(description="The stage identifier of the stage you want to move")
    position: float = Field(description="The position to which you want to move")

class MoveStageResponse(BaseModel):
    success: bool = Field(description="Whether the stage successfully received the move command")
    error: str = Field(description="The error message in case of failure", default=None)

@router.post("/stage/move/")
def moveStage(request: MoveStageRequest) -> MoveStageResponse:
    """
    Moves the indicated stage
    :param request: Request
    :return: Response
    """
    try:
        toplevelinterface.moveStage(request.identifier, request.position)
        return MoveStageResponse(success=True)
    except Exception as error:
        return MoveStageResponse(success=False, error=str(error))