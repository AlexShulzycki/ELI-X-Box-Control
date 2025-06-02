from fastapi import APIRouter, HTTPException
from server import Interface

router = APIRouter(tags=["control"])

@router.get("/get/C884Status")
def getControllerStatus():
    """
    Gets the status of configured C884 controllers
    """
    c884s = Interface.C884interface.c884

    return c884s



# FOR REFERENCE, FOLD THIS INTO THE REST API
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

