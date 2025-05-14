from typing import Dict, Any

from StageControl.C884 import C884


class C884Interface:

    def __init__(self):
        self.c884: dict[int, C884] = {}

    def addC884(self, data):
        self.c884[data["comport"]] = C884(*data)

    async def onTarget(self, comport):
        return await self.c884.get(comport).onTarget()

    async def moveTo(self, comport, axis, target):
        return await self.c884.get(comport).moveTo(axis, target)

    def removeC884(self, comport):
        self.c884.pop(comport).__exit__()

    async def getC884(self, comport:int):
        return self.c884[comport]

    async def getUpdatedC884(self, comport: int):
        return self.c884[comport]

    async def connect(self, comport: int):
        await self.c884[comport].openConnection()
C884interface = C884Interface()
