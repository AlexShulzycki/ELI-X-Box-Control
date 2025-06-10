from fastapi import APIRouter, HTTPException
from server.Interface import Stageinterface
from server.StageControl.DataTypes import StageInfo

router = APIRouter(tags=["control"])

@router.get("/stage/allstageinfo")
def getAllStageInfo() -> list[StageInfo]:
    """
    Gets the status of connected stages
    """

    return Stageinterface.getAllStages()


# TBD if we need a post request to do multiple
@router.get("/stage/stageinfo/{identifier}")
def getStageInfoByIdentifier(identifiers: list[int]) -> StageInfo:
    return Stageinterface.stageInfo(identifiers)



# FOR REFERENCE
# case ReqTypes.connectC884:
#                     res = {"response": "updateC884", "data": C884interface.getUpdatedC884(msg["serial_number"])}
#                     await self.broadcast(res)
#                 case ReqTypes.c884ontarget:
#                     res = {"response": "ontargetPI", "ontarget": C884interface.onTarget(msg["serial_number"]), "serial_number": msg["serial_number"]}
#                     await self.broadcast(res)
#                 case ReqTypes.c884moveto:
#                     C884interface.moveTo(msg["serial_number"], msg["axis"], msg["target"])
#                     res = {"response": "movingPI", "serial_number": msg["serial_number"], "axis": msg["axis"], "target": msg["target"]}
#                     await self.broadcast(res)

