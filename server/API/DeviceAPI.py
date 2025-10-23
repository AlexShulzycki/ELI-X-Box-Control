import asyncio

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field, model_validator

from server import toplevelinterface, ActionRequest
from server.Devices import Device

router = APIRouter(tags=["devices"])

@router.get("/get/devices")
def getAllDevices() -> list[Device]:
    """
    Gets the stage info of connected stages
    :return: dict identifier -> StageInfo
    """
    res = []
    for intf in toplevelinterface.device_interfaces.values():
        res.extend(intf.devices)

    return res

@router.get("/get/refreshdevices")
async def refreshdevices(background_tasks: BackgroundTasks, IDs:list[int] = None) -> None:
    # Run the refresh
    notdone = await toplevelinterface.refreshDevices(IDs)
    # go to sleep :)
    await asyncio.sleep(0.2)
    background_tasks.add_task(refreshdevices, background_tasks, notdone)


class ActionResponse(BaseModel):
    success: bool = True
    message: str|None = None

@router.get("/get/action")
async def getDoAction(action: ActionRequest) -> None:
    toplevelinterface.execute_actions(action)

# TODO Find an efficient way to only have one task rechecking
async def checkUntilFinished(background_tasks: BackgroundTasks, checkIDs: list[int] = None):
    print("Checking until finished ", checkIDs)



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


