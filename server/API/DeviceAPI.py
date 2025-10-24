import asyncio

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field, model_validator

from server import toplevelinterface, ActionRequest
from server.Devices import Device

router = APIRouter(tags=["devices"])

@router.get("/get/devices")
def getAllDevices() -> list[object]:
    """
    Gets the stage info of connected stages
    :return: dict identifier -> StageInfo
    """
    devices: list[Device] = []
    for intf in toplevelinterface.device_interfaces.values():
        devices.extend(intf.devices)

    # serialize
    res = []
    for device in devices:
        res.append(device)
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

@router.post("/post/action")
async def postDoAction(action: ActionRequest) -> None:
    await toplevelinterface.execute_actions([action])



