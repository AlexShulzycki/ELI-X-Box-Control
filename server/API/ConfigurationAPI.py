# This file will take care of communicating via api to select and configure the controllers
import asyncio
import glob
import sys
from typing import Any, Callable

import serial

from fastapi import APIRouter, HTTPException, BackgroundTasks

from pydantic import BaseModel, ValidationError

from server.Interface import toplevelinterface
from server.Settings import SettingsVault
from server.StageControl.DataTypes import updateResponse

router = APIRouter(tags=["configuration"])

@router.get("/get/ConfigState")
def getCurrentConfig():
    """
    Returns current configuration for every interface
    :return:
    """

    res = {}
    for interface in toplevelinterface.interfaces:
        res[interface.name] = interface.currentConfiguration
    return res

@router.get("/get/ConfigSchema")
async def getConfigSchema():
    """
    Returns the schema of congfiguration objects.
    key = controller name (eg pi, virtual, etc), value = its json schema.
    """
    try:
        return await toplevelinterface.configSchema
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/post/UpdateConfiguration", description='{"Virtual": [{"model": "Virtual 1","identifier": 1234,"kind": "linear","minimum": 0,"maximum": 200}]}')
async def updateConfiguration(background_tasks: BackgroundTasks, configuration: dict[str, list[Any]]) -> list[updateResponse]:
    config_finished_check = []
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
                            valid_model = interface.configurationType.model_validate(item)
                            toConfig.append(valid_model)
                            config_finished_check.append(valid_model.SN)
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
                    awaiters = await asyncio.gather(interface.configurationChangeRequest(toConfig))
                    for a in awaiters:
                        res.extend(a)

                except Exception as e:
                    # something catastrophic has happened if that failed
                    print("Catastrophic failure updating configuration", e)
                    raise HTTPException(status_code=500, detail=str(e))

    # Add the configurations we just modified to the check config queue
    background_tasks.add_task(checkUntilConfigured, background_tasks, config_finished_check)
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
            return await cntr.removeConfiguration(identifier)

    # if we are here, we haven't found anything
    raise HTTPException(status_code=404, detail=f"Controller interface {controllername} cannot be found")


class SettingsResponse(BaseModel):
    success: bool
    error: str = None
    configuration: dict[str, Any] = {}

async def getStore(storename: str):
    SV = SettingsVault()
    await SV.load_all()
    if SV.stores.keys().__contains__(storename):
        config = SV.stores[storename]
        return SettingsResponse(success=True, configuration=config)
    else:
        return SettingsResponse(success=False, error="No configurations saved")

@router.get("/get/savedConfigurations")
async def getSavedConfigurations():
    """Returns saved configurations (as from /get/ConfigState) saved on disk"""
    return await getStore("configuration")

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

@router.get("/get/loadConfiguration")
async def getloadConfiguration(name: str):
    """load a configuration from disk"""
    saved = (await getSavedConfigurations()).configuration
    return await updateConfiguration(saved[name])

async def checkUntilConfigured(background_tasks: BackgroundTasks, ids_to_check: list[int]):

    print("checking configs", ids_to_check)
    # go to sleep :)
    await asyncio.sleep(0.2)

    awaiters = []
    for ident in ids_to_check:
        for intf in toplevelinterface.interfaces:
            awaiters.append(intf.is_configuration_configured(ident))

    awaited = await asyncio.gather(*awaiters)
    # flatten array
    check_again = []
    for a in awaited:
        for i in a:
            check_again.append(i)

    if len(check_again) > 0:
        background_tasks.add_task(checkUntilConfigured, background_tasks, check_again)