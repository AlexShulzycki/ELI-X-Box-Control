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
def isReflectionLegal(req: IsReflectionLegalRequest)-> bool:
    """
    Check if reflection is legal
    """
    print(req)

    raise NotImplemented
    return False

@router.post