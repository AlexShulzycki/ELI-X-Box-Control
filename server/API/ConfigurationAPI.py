# This API will take care of communicating via api to select and configure the controllers
import asyncio

from typing import Any, Callable

from fastapi import APIRouter, HTTPException, BackgroundTasks

from pydantic import BaseModel, ValidationError

from server import toplevelinterface
from server.Settings import SettingsVault
from server.Devices.Events import updateResponse

router = APIRouter(tags=["configuration"])

@router.get("/get/ConfigState")
def getCurrentConfig():
    """
    Returns current configuration for every interface
    :return: current configurations
    """
    res = []
    for interface in toplevelinterface.device_interfaces.values():
        res.extend(interface.currentConfigurations)
    return res

@router.get("/get/ConfigSchema")
async def getConfigSchema():
    """
    Returns the schema of congfiguration objects.
    key = controller name (eg pi, virtual, etc), value = its json schema.
    """
    awaiters = []
    for intf in toplevelinterface.device_interfaces.values():
        awaiters.append(intf.configurationSchema)

    return await asyncio.gather(*awaiters)

@router.post("/post/UpdateConfigurations", description='')
async def updateConfiguration(background_tasks: BackgroundTasks, configurations: list[Any]) -> list[updateResponse]:
    config_finished_check = []
    res: list[updateResponse] = []
    to_configure = []

    for config in configurations:
        try:
            intf = toplevelinterface.device_interfaces[config["ControllerType"]]
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(f"Cannot find controller interface, {e}"))

        # try to validate the input into the relevant configuration format
        try:
            valid_model = intf.configurationPydanticModel.model_validate(config)
            to_configure.append(valid_model)
            config_finished_check.append(valid_model.ID)
            # fantastic, we have a valid model, added to queue.
        except ValidationError as e:
            print("Issue parsing configuration: ", e)
            print(f"Configuration in question: {config}")
            raise e

    # all parsed, lets send the requests to their respective interfaces
    to_await = toplevelinterface.updateConfigurations(to_configure)

    # Add the configurations we just modified to the check config queue
    background_tasks.add_task(checkUntilConfigured, background_tasks, config_finished_check)
    res = []
    for awaiter in await to_await:
        res.extend(await awaiter)
    return res

@router.get("/get/RemoveConfiguration")
async def getRemoveConfiguration(configurationid:str,):
    """
    Removes a single configuration from the server
    :return: Success (or not)
    """
    for intf in toplevelinterface.device_interfaces.values():
        if configurationid in intf.configurationIDs:
            return await intf.removeConfiguration(configurationid)

    # if we are here, we did not find anything, hmm
    raise HTTPException(status_code=404, detail=f"Configuration {configurationid} not found")


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
async def getloadConfiguration(background_tasks: BackgroundTasks, name: str):
    """load a configuration from disk"""
    saved = (await getSavedConfigurations()).configuration
    return await updateConfiguration(background_tasks, saved[name])

async def checkUntilConfigured(background_tasks: BackgroundTasks, ids_to_check: list[int]):

    print("checking configs", ids_to_check)
    # go to sleep :)
    await asyncio.sleep(0.2)

    awaiters = []
    for intf in toplevelinterface.device_interfaces:
        awaiters.append(intf.is_configuration_configured(ids_to_check))

    awaited = await asyncio.gather(*awaiters)
    # flatten array
    check_again = []
    for a in awaited:
        for i in a:
            check_again.append(i)

    if len(check_again) > 0:
        background_tasks.add_task(checkUntilConfigured, background_tasks, check_again)