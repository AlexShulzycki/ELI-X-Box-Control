# This file will take care of communicating via api to select and configure the controllers
import glob
import sys
from typing import Any

import serial

from fastapi import APIRouter, HTTPException
import json

from pydantic import BaseModel, Field

from server.Interface import toplevelinterface

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


class currentConfigRes(BaseModel):
    configs: dict[str, list[object]] = Field(description="Dict of controllers mapped to a list containing configuration objects")
@router.get("/get/CurrentConfig")
def getCurrentConfig() -> currentConfigRes:
    """
    Returns current configuration for every interface
    :return:
    """

    res = currentConfigRes(configs = {})
    for interface in toplevelinterface.interfaces:
        res.configs[interface.name] = interface.settings.currentConfiguration
    return res

@router.get("/get/ConfigSchema")
def getConfigSchema():
    """
    Returns the schema of congfiguration objects.
    key = controller name (eg pi, virtual, etc), value = its json schema.
    """
    return toplevelinterface.configSchema

@router.post("/post/UpdateConfiguration")
async def updateConfiguration(configuration):
    awaiters = []
    for name, value in enumerate(configuration):
        for interface in toplevelinterface.interfaces:
            if name == interface.name:
                awaiters.append(interface.settings.configurationChangeRequest(value))

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
