import json
from asyncio import shield
from pathlib import Path
import asyncio

from fastapi.encoders import jsonable_encoder


class SettingsVault:
    """Object that handles saving/loading JSON-formatted settings on disk"""
    def __init__(self, dir_path: str = "settings"):

        self.dir_path: Path = Path(dir_path)
        """Directory for settings files"""
        self._stores: dict[str, object] = {}
        """Dictionary of loaded settings python object representation"""
        #Ensure the settings directory exists
        self.dir_path.mkdir(exist_ok=True)

    @property
    def stores(self) -> dict[str, object]:
        return self._stores

    def updateStore(self, name: str, value: object):
        try:
            json.dumps(jsonable_encoder(value))
        except Exception as e:
            raise Exception("Given object is not JSON serializable")

        # if we are here, we can save the object
        self._stores[name] = value

    async def saveAllToDisk(self):
        """Save all settings to disk"""
        awaiters = []
        for name, value in self._stores.items():
            awaiters.append(self.saveToDisk(name, value))

        await asyncio.gather(*awaiters)

    async def saveToDisk(self, name:str, value:object|str):
        """
        Saves the value to the given store
        :param name: Name of the store to save to
        :param value: python object, or string in json format
        """

        with open(Path(f"{self.dir_path}/{name}.json"), "w+") as f:
            if type(value) == str:
                # if string, write directly
                f.write(value)
            else:
                # if object, dump to string and write that
                f.write(json.dumps(value))
            f.close() # politely close the file

    async def reload_all(self):
        """Removes all stores and loads them in again from disk"""
        self.removeAllStores()
        await self.load_all()

    async def load_all(self):
        """Loads all settings files present on disk"""

        # quick async function for reading
        async def ld(fl: Path):
            try:
                with open(fl) as f:
                    data = json.load(f)
                    f.close()
                self._stores[fl.name[:-5]] = data
            except Exception as e:
                print(f"Failed to load {fl}: {e}")

        # Foreach start off the async reading process and then gather
        awaiters = []
        for file in self.dir_path.glob("*.json"):
            awaiters.append(ld(file))

        await asyncio.gather(*awaiters)

    async def load(self, name: str):
        """Loads given settings from disk"""
        if self.dir_path.glob(f"{name}.json"):
            with open(Path(f"{self.dir_path}/{name}.json")) as f:
                self._stores[name] = json.load(f)
                f.close()
        else:
            raise FileNotFoundError(f"{name} settings not on disk")


    async def purgeUnusedStoresFromDisk(self):
        """Purge unused settings from disk"""
        for file in self.dir_path.glob("*.json"):
            if not self.stores.keys().__contains__(file.name):
                file.unlink()

    def removeStore(self, name):
        if name in self.stores.keys():
            del self.stores[name]
        else:
            raise KeyError(f"{name} is not a store that is currently loaded")

    def removeAllStores(self):
        """Remove all settings stores"""
        self._stores = {}