from pathlib import Path
from unittest import TestCase, IsolatedAsyncioTestCase
import os
from server.Settings import SettingsVault


class TestSettingsVault(IsolatedAsyncioTestCase):

    @classmethod
    def setUp(self):
        self.SV = SettingsVault()

    def test_create(self):
        self.SV.updateStore("test", {"weewoo": True})
        assert self.SV.stores["test"]["weewoo"] is True

    async def test_update(self):
        print(os.getcwd())
        self.SV.updateStore("test", {"weewoo": True})
        assert self.SV.stores["test"]["weewoo"] is True
        await self.SV.saveAllToDisk()
        self.SV.removeAllStores()
        await self.SV.load_all()
        assert self.SV.stores["test"]["weewoo"] is True
        self.SV.updateStore("test2", {"weeweewoowoo": False})
        assert self.SV.stores["test2"]["weeweewoowoo"] is False
        assert self.SV.stores["test"]["weewoo"] is True

    async def test_delete(self):
        # load in values
        self.SV.updateStore("test", {"weewoo": True})
        self.SV.updateStore("test2", {"weeweewoowoo": False})
        # assert they're there
        assert self.SV.stores["test2"]["weeweewoowoo"] is False
        assert self.SV.stores["test"]["weewoo"] is True
        # save, remove, reload
        await self.SV.saveAllToDisk()
        await self.SV.reload_all()
        # assert they're there
        assert self.SV.stores["test2"]["weeweewoowoo"] is False
        assert self.SV.stores["test"]["weewoo"] is True
        # remove one
        self.SV.removeStore("test2")
        # assert its not there
        assert not self.SV.stores.keys().__contains__("test2")
        # reload (we still have it saved to the file, so we get it back)
        await self.SV.load_all()
        # assert its there again, then remove it again
        assert self.SV.stores["test2"]["weeweewoowoo"] is False
        self.SV.removeStore("test2")
        # purge unused files (should delete the file this time)
        await self.SV.purgeUnusedStoresFromDisk()
        # remove all stores and reload
        await self.SV.reload_all()
        # assert the purged store is not there
        assert not self.SV.stores.keys().__contains__("test2")

    def test_unjsonable(self):
        unjsonable_data = {"cigarette": [type(int)]}
        with self.assertRaises(Exception):
            self.SV.updateStore("nicotine", unjsonable_data)

    @classmethod
    def tearDown(self):
        # remove everything
        if Path("settings").is_dir():
            for file in Path("settings").glob("*"):
                file.unlink()
        Path("settings").rmdir()