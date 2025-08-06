# This file will take care of communicating via api to select and configure the controllers
import asyncio
import glob
import sys
from typing import Any, Awaitable

import serial

from fastapi import APIRouter, HTTPException
import json

from pydantic import BaseModel, Field, ValidationError

from server.Interface import toplevelinterface
from server.Settings import SettingsVault
from server.StageControl.DataTypes import updateResponse

router = APIRouter(tags=["configuration"])


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
                    try:
                        # try to validate the input into the relevant configuration format
                        try:
                            valid_model = interface.settings.configurationFormat.model_validate(item)
                            toConfig.append(valid_model)
                        except ValidationError as e:
                            print("Issue parsing config: ", e)
                            print(item)
                            raise e
                    except Exception as e:
                        # Bad validation format, add as error
                        res.append(updateResponse(
                            identifier=-5, # some random identifier to pass the pydantic check
                            success=False,
                            error=str(e),
                        ))
                        # move on, this will skip adding the current (malformed) configuration and add the error response to the response list
                        continue
                try:
                    # Try configuring the objects, and collect their update responses to the response list
                    awaiters = await asyncio.gather(interface.settings.configurationChangeRequest(toConfig))
                    for a in awaiters:
                        res.extend(a)

                except Exception as e:
                    # something catastrophic has happened if that failed
                    print("Catastrophic failure updating configuration", e)
                    raise HTTPException(status_code=500, detail=str(e))
    return res

@router.get("/get/RemoveConfiguration")
async def getRemoveConfiguration(controllername:str, identifier:int):
    """
    Removes a single configuration from the server
    :return: Success (or not)
    """
    for cntr in toplevelinterface.interfaces:
        if cntr.name == controllername:
            # we found the correct controller, run the command
            return await cntr.settings.removeConfiguration(identifier)

    # if we are here, we haven't found anything
    raise HTTPException(status_code=404, detail=f"Controller interface {controllername} cannot be found")


class SettingsResponse(BaseModel):
    success: bool
    error: str = None
    configuration: dict[str, Any] = {}

@router.get("/get/savedConfigurations")
async def getSavedConfigurations():
    """Returns saved configurations (as from /get/ConfigState) saved on disk"""
    SV = SettingsVault()
    await SV.load_all()
    if SV.stores.keys().__contains__("configuration"):
        config = SV.stores["configuration"]
        return SettingsResponse(success=True, configuration=config)
    else:
        return SettingsResponse(success=False, error="No configurations saved")

@router.get("/get/saveCurrentConfiguration")
async def getSaveCurrentConfiguration(name: str):
    """Saves the current configuration (as from /get/ConfigState) to disk under the given name"""
    # load in the saved configuration
    loaded = await getSavedConfigurations()
    if not loaded.success and loaded.error != "No configurations saved":
        return loaded

    # if we are here its loaded correctly
    to_save = loaded.configuration
    to_save[name] = getCurrentConfig()
    # save to disk
    try:
        SV = SettingsVault()
        await SV.saveToDisk("configuration", to_save)
        return SettingsResponse(success=True, configuration = to_save)
    except Exception as e:
        return SettingsResponse(success=False, error=str(e))

@router.get("/get/removeSavedConfiguration")
async def getRemoveSavedConfiguration(name: str):
    """Removes a saved configuration from disk"""
    # load in the saved configuration
    loaded = await getSavedConfigurations()
    if not loaded.success:
        return loaded

    if not loaded.configuration.keys().__contains__(name):
        return SettingsResponse(success=False, error=f"No saved configuration under name {name} found")

    try:
        del loaded.configuration[name]
        SV = SettingsVault()
        await SV.saveToDisk("configuration", loaded.configuration)
        return SettingsResponse(success=True, configuration=loaded.configuration)
    except Exception as e:
        return SettingsResponse(success=False, error=str(e))