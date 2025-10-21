import asyncio

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field, model_validator

from server import toplevelinterface
from server.Devices.DataTypes import StageInfo, StageStatus, StageKind

router = APIRouter(tags=["control"])

@router.get("/get/devices")
def getAllDevices() -> dict[int, StageInfo]:
    """
    Gets the stage info of connected stages
    :return: dict identifier -> StageInfo
    """
    return toplevelinterface.devices

@router.get("/get/refreshdevices")
async def refreshdevices(background_tasks: BackgroundTasks, IDs:list[int] = None) -> None:
    await toplevelinterface.refresh_devices(IDs)
    background_tasks.add_task(checkUntilFinished, background_tasks, IDs)


class ActionResponse(BaseModel):
    success: bool = True
    message: str|None = None

@router.get("/get/action")
async def getDoAction(identifier: int, action: str, value: str|float|bool|None) -> None:
    toplevelinterface.doAction(identifier, action, value)

# TODO Find an efficient way to only have one task rechecking
async def checkUntilFinished(background_tasks: BackgroundTasks, checkIDs: list[int] = None):
    print("Checking until finished ", checkIDs)

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
    background_tasks.add_task(checkUntilFinished, background_tasks, toUpdate)


