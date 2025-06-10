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


def doesSerialNumberExist(serial_number: int):
    """
    Checks if serial number is a key in the configuration, if so, returns true, else raises an HTTPException.
    :param serial_number: Serial number to check
    :return: True if exists, exception is raised otherwise
    """
    if Interface.C884interface.c884.keys().__contains__(serial_number):
        return True
    else:
        raise HTTPException(status_code=405, detail="Serial number not found in configuration")


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


@router.get("/pi/supportedStages/{serial_number}")
async def getSupportedStages(serial_number: int):
    doesSerialNumberExist(serial_number)

    try:
        return await Interface.C884interface.c884[serial_number].getSupportedStages()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pi/enumerateUSB/")
async def getEnumUSB():
    return await Interface.EnumPIUSB()


@router.get("/get/StageAxisInfo")
def getSavedStageAxisTypes():
    try:
        with open('../settings/stageinfo/PIStages.json') as f:
            PIStages = json.load(f)
            f.close()
        with open('../settings/stageinfo/Axes.json') as f:
            Axes = json.load(f)
            f.close()
        with open("../settings/stageinfo/StandaStages.json") as f:
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
    with open("../settings/StageConfig.json") as f:
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


@router.post("/pi/AddRS232")
async def piAddRS232(config: C884RS232Config) -> int:
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
    if doesSerialNumberExist(serial_number):
        Interface.C884interface.removeC884(serial_number)


@router.get("/get/SaveCurrentStageConfig")
async def getSaveCurrentStageConfig():
    """
    Saves current stage configuration on the server to settings/StageConfig.json
    """
    # Grab configuration data from the interfaces TODO FIX
    config = await getCurrentConfig()
    config = config.model_dump_json()

    with open("../settings/StageConfig.json", "w") as f:
        f.write(config)
        f.close()


@router.get("/pi/Connect/{serial_number}")
async def piConnectC884(serial_number: int) -> bool:
    if doesSerialNumberExist(serial_number):
        try:
            return await Interface.C884interface.connect(serial_number)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


@router.get("/pi/Status/")
async def getPIStatus() -> list[C884Status]:
    return await Interface.C884interface.getC884Status()


@router.get("/pi/getRange/{serial_number}", response_model=list[list[float]])
async def getPIRange(serial_number: int):
    if doesSerialNumberExist(serial_number):
        return await Interface.C884interface.c884[serial_number].range
