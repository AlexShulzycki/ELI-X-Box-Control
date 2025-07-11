from fastapi import APIRouter, HTTPException

from pydantic import BaseModel, Field

import server.StageControl.Virtual
from server import Interface

router = APIRouter(tags=["settings", "virtual"])

def doesVirtualSNexist(sn) -> bool:
    if getVirtualStages().__contains__(sn):
        return True
    else:
        return False

@router.get("/virtual/getAll")
def getVirtualStages():
    return Interface.Virtualinterface.stages


@router.get("/virtual/getInfo/{serial_number}")
def getVirtualStagesInfo(serial_number: int):

    if not doesVirtualSNexist(serial_number):
        raise HTTPException(status_code=404, detail=f"SN {serial_number} doesn't exist")

    return Interface.Virtualinterface.stageInfo([serial_number])


@router.get("/virtual/getStatus/{serial_numbers}")
def getVirtualStatusInfo(serial_number: int):

    if not doesVirtualSNexist(serial_number):
        raise HTTPException(status_code=404, detail=f"SN {serial_number} doesn't exist")

    return Interface.Virtualinterface.stageStatus([serial_number])


@router.post("/virtual/addStage")
def postAddStage(stages: list[server.StageControl.DataTypes.StageInfo]):
    print(stages)
    Interface.Virtualinterface.addStagesbyConfigs(stages)
    return getVirtualStages()

@router.get("/virtual/remove/{sn}")
def getremovestage(sn: int) -> bool:
    """Removes virtual stage by its unique serial number"""
    if doesVirtualSNexist(sn):
        res = Interface.Virtualinterface.removeStage(sn)
    return res
