from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from server import Interface
from server.StageControl.C884 import C884Config, C884RS232Config, C884Status

router = APIRouter(tags=["settings", "PI"])



def doesPISerialNumberExist(serial_number: int):
    """
    Checks if serial number is a key in the configuration, if so, returns true, else raises an HTTPException.
    :param serial_number: Serial number to check
    :return: True if exists, exception is raised otherwise
    """
    if Interface.C884interface.c884.keys().__contains__(serial_number):
        return True
    else:
        raise HTTPException(status_code=405, detail="Serial number not found in configuration")

@router.get("/pi/supportedStages/{serial_number}")
async def getSupportedStages(serial_number: int):
    doesPISerialNumberExist(serial_number)

    try:
        return await Interface.C884interface.c884[serial_number].getSupportedStages()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pi/enumerateUSB/")
async def getEnumUSB():
    return await Interface.EnumPIUSB()


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
    if doesPISerialNumberExist(serial_number):
        Interface.C884interface.removeC884(serial_number)


@router.get("/pi/Connect/{serial_number}")
async def piConnectC884(serial_number: int) -> bool:
    if doesPISerialNumberExist(serial_number):
        try:
            return await Interface.C884interface.connect(serial_number)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


@router.get("/pi/Status/")
async def getPIStatus() -> list[C884Status]:
    return await Interface.C884interface.getC884Status()


@router.get("/pi/getRange/{serial_number}", response_model=list[list[float]])
async def getPIRange(serial_number: int):
    if doesPISerialNumberExist(serial_number):
        return await Interface.C884interface.c884[serial_number].range

@router.get("/pi/LoadStagesToC884/{serial_number}")
async def loadStagesToC884(serial_number: int):
    if doesPISerialNumberExist(serial_number):
        return await Interface.C884interface.c884[serial_number].loadStagesToC884()

@router.get("/pi/enableCLO/{serial_number_channel}")
async def enableCLO(serial_number_channel: int):
    interface = Interface.C884interface
    await interface.enableCLO(serial_number_channel)