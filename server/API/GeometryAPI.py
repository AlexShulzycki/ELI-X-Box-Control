from enum import Enum

from fastapi import APIRouter, HTTPException
from server import Interface
from pydantic import BaseModel, Field

from server.Calculations.DataTypes import Element, elements, Crystal, crystals

router = APIRouter(tags=["calculation", "geometry"])

class VonHamosRequest(BaseModel):
    element_symbol: str = Field(description="Element symbol", examples=["Cu", "Fe"])

class IsReflectionLegalRequest(BaseModel):
    element: Element

@router.post("/geometry/isReflectionLegal")
def isReflectionLegal(req: IsReflectionLegalRequest)-> bool:
    """
    Check if reflection is legal
    """
    print(req)

    raise NotImplemented
    return False

@router.get("/geometry/ElementData")
def getElementData() -> dict[str, Element]:
    """Returns a dict of Element objects with their emission/absorption lines from /data/"""
    return elements

@router.get("/geometry/CrystalData")
def getCrystalData() -> list[Crystal]:
    """Returns a list of Crystal objects loaded from /data/"""
    return crystals