import asyncio
from collections.abc import Coroutine

from StageControl.C884 import C884
from server.StageControl.C884 import C884Config


class C884Interface:

    def __init__(self):
        self.c884: dict[int, C884] = {}

    def addC884(self, data):
        self.c884[data["comport"]] = C884(*data)

    async def onTarget(self, comport):
        return self.c884.get(comport).onTarget()

    async def moveTo(self, comport, axis, target):
        return self.c884.get(comport).moveTo(axis, target)

    def removeC884(self, comport):
        self.c884.pop(comport).__exit__()

    def getC884(self, comport:int):
        return self.c884[comport]

    async def updateC884Configs(self, configs: [C884Config]):
        """
        Update the c884s with these configs
        :param configs: array of C884Config objects
        :return:
        """
        awaiters: [Coroutine] = []
        for config in configs:
            if self.c884.keys().__contains__(config.comport):
                awaiters.append(self.c884[config.comport].updateConfig(config))
            else:
                self.c884.update({config.comport: C884(config)})
        await asyncio.gather(*awaiters)

    def getC884Configs(self) -> list[C884Config]:
        # Collect configs from each c884
        res: list[C884Config] = []
        for com, c884 in self.c884.items():
            res.append(c884.getConfig())
        return res

    async def connect(self, comport: int):
        """
        Attempt to connect to a C884 on the given com port
        :param comport: comport to try
        :return:
        """
        await self.c884[comport].openConnection()


C884interface = C884Interface()

