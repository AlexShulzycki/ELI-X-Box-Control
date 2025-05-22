# This file will take care of communicating via api to select and configure the controllers
from typing import Annotated

from fastapi import APIRouter, HTTPException
import json

from pydantic import BaseModel, Field, TypeAdapter

import Interface
from server.StageControl.C884 import C884Config


class StageConfig(BaseModel):
    C884: list[C884Config] = Field(default=[], examples=[[C884Config(comport=15)]])

router = APIRouter()

@router.get("/get/comports")
def getComPorts():
    comports = []
    return comports

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

@router.get("/pi/RemoveConfigOnPort/{comport}")
def piRemoveConfigOnPort(comport: int):
    """
    Removes c884 controller from config as well as shutting it down/disconnecting etc.
    :param comport:
    :return:
    """
    if not Interface.C884interface.c884.__contains__(comport):
        raise HTTPException(status_code=404, detail="No such comport configured")
    else:
        Interface.C884interface.removeC884(comport)

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

@router.get("/pi/ConnectC884/{comport}")
async def piConnectC884(comport: int):
    if not Interface.C884interface.c884.__contains__(comport):
        raise HTTPException(status_code=404, detail="No such comport configured")
    else:
        await Interface.C884interface.connect(comport)

