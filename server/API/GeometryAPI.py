from enum import Enum

from fastapi import APIRouter, HTTPException
from server import Interface
from pydantic import BaseModel, Field

router = APIRouter(tags=["calculation", "geometry"])

class Element(Enum):
    Cu = "Cu"

class IsReflectionLegalRequest(BaseModel):
    element: Element

@router.get("/post/isReflectionLegal")
def isReflectionLegal()-> bool:
    """
    Gets the status of configured C884 controllers
    """
    c884s = Interface.C884interface.c884

    return c884s