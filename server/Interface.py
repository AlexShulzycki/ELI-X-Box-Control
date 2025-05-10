from StageControl import C884 as C884


class C884Interface:

    def __init__(self):
        self.c884: dict[int: C884] = {}

    async def getC884(self, comport:int):
        return self.c884[comport]

    async def getUpdatedC884(self, comport: int):
        return self.c884[comport]

C884interface = C884Interface()
