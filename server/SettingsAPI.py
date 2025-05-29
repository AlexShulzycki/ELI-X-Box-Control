# This file will take care of communicating via api to select and configure the controllers
from typing import Annotated

from fastapi import APIRouter, HTTPException
import json

from pydantic import BaseModel, Field, TypeAdapter

from . import Interface
from .Interface import C884interface
from .StageControl.C884 import C884Config, C884RS232Config, C884Status


class StageConfig(BaseModel):
    C884: list[C884Config | C884RS232Config] = Field(default=[], examples=[[C884RS232Config(comport=15)]])


router = APIRouter()


@router.get("/get/comports")
def getComPorts():
    comports = []
    return comports


@router.get("/pi/enumerateUSB/")
async def getEnumUSB():
    return await Interface.EnumPIUSB()


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

    return StageConfig(C884=c884configs)


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


@router.post("/pi/AddRS232")
async def piAddRS232(config: C884RS232Config):
    """
    Adds and connects via RS232 - on successful connection, reads serial number, saves in config
    :param config:
    :return: serial number if connected successfully
    """
    try:
        return await Interface.C884interface.addC884RS232(config)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pi/RemoveBySerialNumber/{serial_number}")
def piRemoveBySerialNumber(serial_number: int):
    """
    Removes c884 controller as well as shutting it down/disconnecting etc.
    :param serial_number:
    :return:
    """
    if not Interface.C884interface.c884.keys().__contains__(serial_number):
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


@router.get("/pi/Connect/{serial_number}")
async def piConnectC884(serial_number: int) -> bool:
    if not Interface.C884interface.c884.keys().__contains__(serial_number):
        raise HTTPException(status_code=404, detail="No such serial_number configured")
    else:
        try:
            return await Interface.C884interface.connect(serial_number)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

@router.get("/pi/Status/")
async def getPIStatus() -> list[C884Status]:
    return await Interface.C884interface.getC884Status()