# This file will take care of communicating via api to select and configure the controllers
import glob
import sys
import serial

from fastapi import APIRouter, HTTPException
import json

from pydantic import BaseModel, Field

from server import Interface
from server.StageControl.C884 import C884Config, C884RS232Config, C884Status


class StageConfig(BaseModel):
    C884: list[C884Config | C884RS232Config] = Field(default=[], examples=[[C884RS232Config(comport=15)]])


router = APIRouter(tags=["settings"])


@router.get("/get/comports")
def getComPorts() -> list[int]:
    """
    Lists serial port names. Stolen from https://stackoverflow.com/a/14224477
    :raises EnvironmentError:
        On unsupported or unknown platforms
    :returns:
        A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(int(port[3:]))  # only return the com port number
        except (OSError, serial.SerialException):
            pass
    return result





@router.get("/get/StageAxisInfo")
def getSavedStageAxisTypes():
    try:
        with open('../../settings/stageinfo/PIStages.json') as f:
            PIStages = json.load(f)
            f.close()
        with open('../../settings/stageinfo/Axes.json') as f:
            Axes = json.load(f)
            f.close()
        with open("../../settings/stageinfo/StandaStages.json") as f:
            StandaStages = json.load(f)
            f.close()

        return {
            "Stages": {"PI": PIStages, "Standa": StandaStages},
            "Axes": Axes,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get/SavedStageConfig")
def getSavedStageSettings() -> StageConfig:
    """
    Returns saved stage configuration loaded from settings/StageConfig.json
    @return: JSON object saved in SavedMotorSettings.py
    """
    # Load from file
    with open("../../settings/StageConfig.json") as f:
        settings: StageConfig = json.load(f)
        f.close()

    return settings


@router.get("/get/CurrentConfig")
async def getCurrentConfig() -> StageConfig:
    """
    Get current stage configuration running on the server
    """
    # Dump each C884 BaseModel into dict to avoid passing in a BaseModel into StageConfig, which is also BaseModel
    c884configs = []
    for c884 in Interface.C884interface.getC884Configs():
        c884configs.append(c884.model_dump())

    return StageConfig(C884=c884configs)


@router.post("/post/UpdateConfig")
async def updateConfig(data: StageConfig):
    """
    Update received stage configurations
    """
    print("Received updated stage config: ", data)
    try:
        await Interface.C884interface.updateC884Configs(data.C884)
        return await getCurrentConfig()

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.get("/get/SaveCurrentStageConfig")
async def getSaveCurrentStageConfig():
    """
    Saves current stage configuration on the server to settings/StageConfig.json
    """
    # Grab configuration data from the interfaces TODO FIX
    config = await getCurrentConfig()
    config = config.model_dump_json()

    with open("../../settings/StageConfig.json", "w") as f:
        f.write(config)
        f.close()
