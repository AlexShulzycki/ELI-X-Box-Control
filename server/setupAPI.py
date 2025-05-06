# This file will take care of communicating via api to select and configure the controllers
from fastapi import APIRouter
import json

router = APIRouter()

@router.get("/comports")
def getComPorts():
    comports = []
    return comports

@router.get("/stageaxistypes")
def getStageAxisTypes():
    PIstageList = []
    axesList = []
    standaconfigs = []
    with open('data/StageInformation/PIStageList.txt') as f:
        for line in f.readlines():
            PIstageList.append(line.strip())  # strip() to get rid of \n characters
        f.close()
    with open('data/StageInformation/AxesList.txt') as f:
        for line in f.readlines():
            axesList.append(line.strip())  # strip() to get rid of \n characters
        f.close()
    with open("data/StageInformation/StandaConfigs.json") as f:
        standaconfigs = json.load(f)
        f.close()

    return {
        "PI": PIstageList,
        "Axes": axesList,
        "Standa": standaconfigs.keys()
    }

@router.get("/stagesettings")
def getStageSettings():
    """
    Loads previous motor and controller setup settings from assets/SavedMotorSettings.py
    @return: JSON object saved in SavedMotorSettings.py
    """
    # Load from file
    with open("data/StageInformation/SavedMotorSettings.json") as f:
        settings = json.load(f)
        f.close()

    return settings

