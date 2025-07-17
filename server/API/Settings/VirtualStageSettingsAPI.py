from fastapi import APIRouter, HTTPException

from pydantic import BaseModel, Field

import server.StageControl.Virtual
from server.Interface import Virtualinterface as interface

router = APIRouter(tags=["settings", "virtual"])

def doesVirtualSNexist(sn) -> bool:
    if getVirtualStages().__contains__(sn):
        return True
    else:
        return False

@router.get("/virtual/getAll")
def getVirtualStages():
    return interface.stages


@router.get("/virtual/getInfo/{serial_number}")
def getVirtualStagesInfo(serial_number: int):

    if not doesVirtualSNexist(serial_number):
        raise HTTPException(status_code=404, detail=f"SN {serial_number} doesn't exist")

    return interface.stageInfo[serial_number]


@router.get("/virtual/getStatus/{serial_numbers}")
def getVirtualStatusInfo(serial_number: int):

    if not doesVirtualSNexist(serial_number):
        raise HTTPException(status_code=404, detail=f"SN {serial_number} doesn't exist")

    return interface.stageStatus[serial_number]


@router.post("/virtual/addStages")
def postAddStages(stages: list[server.StageControl.DataTypes.StageInfo]):

    try:
        interface.addStagesByConfigs(stages)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return getVirtualStages()

@router.get("/virtual/remove/{sn}")
def getremovestage(sn: int) -> bool:
    """Removes virtual stage by its unique serial number"""
    if not doesVirtualSNexist(sn):
        raise HTTPException(status_code=404, detail=f"SN {sn} doesn't exist")

    res = interface.removeStage(sn)
    return res
