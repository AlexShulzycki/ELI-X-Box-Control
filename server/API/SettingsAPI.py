# This file will take care of communicating via api to select and configure the controllers
import asyncio
import glob
import sys
from typing import Any, Awaitable

import serial

from fastapi import APIRouter, HTTPException
import json

from pydantic import BaseModel, Field

from server.Interface import toplevelinterface
from server.StageControl.DataTypes import updateResponse

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


@router.get("/get/SavedStageConfig")
def getSavedStageSettings() -> None:
    """
    Does nothing
    @return: nothing
    """
    # Load from file
    with open("../settings/StageConfig.json") as f:
#        settings: StageConfig = json.load(f)
        f.close()

    return None

@router.get("/get/ConfigState")
def getCurrentConfig():
    """
    Returns current configuration for every interface
    :return:
    """

    res = {}
    for interface in toplevelinterface.interfaces:
        res[interface.name] = interface.settings.currentConfiguration
    return res

@router.get("/get/ConfigSchema")
def getConfigSchema():
    """
    Returns the schema of congfiguration objects.
    key = controller name (eg pi, virtual, etc), value = its json schema.
    """
    try:
        return toplevelinterface.configSchema
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/post/UpdateConfiguration", description='{"Virtual": [{"model": "Virtual 1","identifier": 1234,"kind": "linear","minimum": 0,"maximum": 200}]}')
async def updateConfiguration(configuration: dict[str, list[Any]]) -> list[updateResponse]:
    res: list[updateResponse] = []
    for name, array in configuration.items():
        for interface in toplevelinterface.interfaces:
            if name == interface.name:
                toConfig = []
                # convert each entry to appropriate configuration object
                for item in array:
                    toConfig.append(interface.settings.configurationFormat.model_validate(item))
                try:
                    # Try configuring the objects, and collect their update responses to the response list
                    res.extend(interface.settings.configurationChangeRequest(toConfig))
                except Exception as e:
                    # something catastrophic has happened if that failed
                    raise HTTPException(status_code=500, detail=str(e))
    return res

@router.get("/get/SaveCurrentStageConfig")
async def getSaveCurrentStageConfig():
    """
    Does nothing right now.
    Saves current stage configuration on the server to settings/StageConfig.json
    """
    # Grab configuration data from the interfaces TODO FIX
    #config = await getCurrentConfig()
    #config = config.model_dump_json()

    with open("../settings/StageConfig.json", "w") as f:
        #f.write(config)
        f.close()

@router.get("/get/RemoveConfiguration")
async def getRemoveConfiguration(controllername:str, identifier:int):
    """
    Removes a single configuration from the server
    :return: Success (or not)
    """
    for cntr in toplevelinterface.interfaces:
        if cntr.name == controllername:
            # we found the correct controller, run the command
            return cntr.settings.removeConfiguration(identifier)

    # if we are here, we haven't found anything
    raise HTTPException(status_code=404, detail=f"Controller interface {controllername} cannot be found")
