from enum import Enum

from fastapi import APIRouter, HTTPException
from server import Interface
from pydantic import BaseModel, Field

from server.Calculations.DataTypes import Element, elements, Crystal, crystals
from server.Calculations.VonHamos import Alignment

router = APIRouter(tags=["calculation", "geometry"])


@router.get("/get/geometry/ElementData")
def getElementData() -> dict[str, Element]:
    """Returns a dict of Element objects with their emission/absorption lines from /data/"""
    return elements


@router.get("/get/geometry/CrystalData")
def getCrystalData() -> dict[str, Crystal]:
    """Returns a list of Crystal objects loaded from /data/"""
    return crystals


@router.get("/get/geometry/Alignment")
def getAlignment(element: str, crystal: str, order: int = 5, height: int = 250) -> Alignment:
    """Returns an Alignment object. Height refers to the distance between detector and crystal in the y axis, i.e. the hight of the isosceles triangle"""

    if not crystals.keys().__contains__(crystal):
        raise HTTPException(status_code=404, detail=f"crystal {crystal} not found")

    if not elements.__contains__(element):
        raise HTTPException(status_code=404, detail=f"element {element} not found")

    return Alignment(
        element=elements[element],
        crystal=crystals[crystal],
        order=order,
        height=height
    )

@router.get("/get/geometry/ManualAlignment")
def getManualAlignment(element: Element, crystal: Crystal, order: int = 5, height: int = 250) -> Alignment:
    return Alignment(
        element=element,
        crystal=crystal,
        order=order,
        height=height
    )