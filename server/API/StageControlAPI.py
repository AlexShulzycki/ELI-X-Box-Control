import asyncio

from fastapi import APIRouter, HTTPException, BackgroundTasks
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


async def checkUntilOnTarget(background_tasks: BackgroundTasks, checkIDs: list[int] = None):
    print("checkuntilontarget for ", checkIDs)

    # go to sleep :)
    await asyncio.sleep(0.2)

    if checkIDs is None:
        checkIDs = toplevelinterface.allIdentifiers
    elif len(checkIDs) == 0:
        # If there's nothing to check, then don't check :)
        return

    # Refresh relevant statuses
    await toplevelinterface.updateStageStatus(checkIDs)

    # Construct a list of IDs that aren't on target
    toUpdate: list[int] = []
    # Check if we are on target
    print(toplevelinterface.StageStatus)
    for id in checkIDs:
        if not toplevelinterface.StageStatus[id].ontarget:
            toUpdate.append(id)

    # reschedule the task - since we are passing IDs we know are not on target, the list will naturally dwindle
    background_tasks.add_task(checkUntilOnTarget, background_tasks, toUpdate)


@router.get("/get/stage/update/status")
async def updateStageStatus(background_tasks: BackgroundTasks, identifiers: list[int] = None):
    """
    Updates the status of all connected stages
    """
    await toplevelinterface.updateStageStatus(identifiers=identifiers)
    background_tasks.add_task(checkUntilOnTarget, background_tasks)
    return


@router.get("/get/stage/update/info")
async def updateStageInfo(background_tasks: BackgroundTasks, identifiers: list[int] = None):
    """
    Updates the info of all connected stages
    """
    await toplevelinterface.updateStageInfo()
    background_tasks.add_task(checkUntilOnTarget, background_tasks, identifiers)
    return

class FullState(BaseModel):
    identifier: int
    model: str
    kind: StageKind
    minimum: float
    maximum: float
    connected: bool
    ready: bool
    position: float
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


@router.get("/get/stage/move")
async def moveStage(background_tasks: BackgroundTasks, identifier: int, position: float) -> MoveStageResponse:
    """
    Moves the indicated stage
    :return: Response
    """
    try:
        await toplevelinterface.moveStage(identifier, position)
        background_tasks.add_task(checkUntilOnTarget, background_tasks, [identifier])
        return MoveStageResponse(success=True)
    except Exception as error:
        return MoveStageResponse(success=False, error=str(error))


@router.get("/get/stage/step")
async def stepStage(background_tasks: BackgroundTasks, identifier: int, step: float) -> MoveStageResponse:
    try:
        await toplevelinterface.stepStage(identifier, step)
        background_tasks.add_task(checkUntilOnTarget, background_tasks, [identifier])
        return MoveStageResponse(success=True)
    except Exception as error:
        return MoveStageResponse(success=False, error=str(error))
