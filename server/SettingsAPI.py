# This file will take care of communicating via api to select and configure the controllers
from typing import Annotated

from fastapi import APIRouter, HTTPException
import json

from pydantic import BaseModel, Field, TypeAdapter

from . import Interface
from .StageControl.C884 import C884Config, C884RS232Config

class StageConfig(BaseModel):
    C884: list[C884Config] = Field(default=[], examples=[[C884RS232Config(comport=15)]])

router = APIRouter()

@router.get("/get/comports")
def getComPorts():
    comports = []
    return comports

@router.get("/get/enumerateUSB")
async def getEnumUSB():
    return await Interface.EnumC884USB()

@router.get("/get/StageAxisInfo")
def getSavedStageAxisTypes():

    try:
        with open('settings/stageinfo/PIStages.json') as f:
            PIStages = json.load(f)
            f.close()
        with open('settings/stageinfo/Axes.json') as f:
            Axes = json.load(f)
            f.close()
        with open("settings/stageinfo/StandaStages.json") as f:
            StandaStages = json.load(f)
            f.close()

        return {
                "Stages": {"PI": PIStages, "Standa": StandaStages},
                "Axes": Axes,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/get/SavedStageConfig")
def getStageSettings() -> StageConfig:
    """
    Returns saved stage configuration loaded from settings/StageConfig.json
    @return: JSON object saved in SavedMotorSettings.py
    """
    # Load from file
    with open("settings/StageConfig.json") as f:
        settings: StageConfig = json.load(f)
        f.close()

    return settings


@router.get("/get/StageConfig")
async def getStageConfig() -> StageConfig:
    """
    Get current stage configuration running on the server
    """
    # Dump each C884 BaseModel into dict to avoid passing in a BaseModel into StageConfig, which is also BaseModel
    c884configs = []
    for c884 in Interface.C884interface.getC884Configs():
        c884configs.append(c884.model_dump())

    return StageConfig(C884 = c884configs)

@router.post("/post/updateStageConfig")
async def updateStageConfig(data: StageConfig):
    """
    Update received stage configurations
    """
    print("Received updated stage config: ", data)
    try:
        await Interface.C884interface.updateC884Configs(data.C884)
        return await getStageConfig()

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/pi/RemoveC884BySerialNumber/{serial_number}")
def piRemoveConfigOnPort(serial_number: int):
    """
    Removes c884 controller as well as shutting it down/disconnecting etc.
    :param serial_number:
    :return:
    """
    if not Interface.C884interface.c884.__contains__(serial_number):
        raise HTTPException(status_code=404, detail="No such serial_number configured")
    else:
        Interface.C884interface.removeC884(serial_number)

@router.get("/get/SaveCurrentStageConfig")
async def getSaveCurrentStageConfig():
    """
    Saves current stage configuration on the server to settings/StageConfig.json
    """
    # Grab configuration data from the interfaces TODO FIX
    config = await getStageConfig()
    config = config.model_dump_json()

    with open("settings/StageConfig.json", "w") as f:
        f.write(config)
        f.close()

@router.get("/pi/ConnectC884/{serial_number}")
async def piConnectC884(serial_number: int)-> bool:
    if not Interface.C884interface.c884.__contains__(serial_number):
        raise HTTPException(status_code=404, detail="No such serial_number configured")
    else:
        return await Interface.C884interface.connect(serial_number)

