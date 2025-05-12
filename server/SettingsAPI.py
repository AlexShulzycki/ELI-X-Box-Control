# This file will take care of communicating via api to select and configure the controllers
from fastapi import APIRouter, HTTPException
import json
import Interface

router = APIRouter()

@router.get("/get/comports")
def getComPorts():
    comports = []
    return comports

@router.get("/get/SavedStagesAxes")
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
def getStageSettings():
    """
    Loads previous motor and controller setup settings from assets/SavedMotorSettings.py
    @return: JSON object saved in SavedMotorSettings.py
    """
    # Load from file
    try:
        with open("settings/StageConfig.json") as f:
            settings = json.load(f)
            f.close()

        return settings
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/get/ControllerStatus")
async def getControllerStatus():
    """
    Gets the status of the controllers connected
    """

    return await Interface.C884interface.getUpdatedC884()

@router.post("/post/updateStageConfig")
async def updateStageConfig(data):
    """
    Update received stage configurations
    """
    print("Received updated stage config: ", data)
    try:
        data = json.load(data)
        return True
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


