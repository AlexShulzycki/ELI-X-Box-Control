from fastapi import APIRouter, HTTPException

from pydantic import BaseModel, Field

from server import Interface


router = APIRouter(tags=["settings"])