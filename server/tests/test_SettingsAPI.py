import unittest

import fastapi.encoders
from fastapi.testclient import TestClient
from server.main import app
from server.Interface import C884interface
from server.StageControl.PI.C884 import C884Config, C884RS232Config
from server.API.SettingsAPI import StageConfig


client = TestClient(app)

# OUTDATED, REWRITE PLEASE

class SettingsAPITest(unittest.TestCase):

    def test_get_stage_config(self):
        """
        Test if we have an empty list :)
        :return:
        """
        response = client.get("/get/CurrentConfig")
        print(response.json())
        assert response.status_code == 200
        assert str(response.json()["C884"]) == str(C884interface.getC884Configs())

    def test_add_sn_config(self):
        """
        Add a controller with serial number, check that it is configured correctly
        :return:
        """
        snconfig = C884Config(serial_number = 12345)
        stageconfig = StageConfig()
        stageconfig.C884.append(snconfig)
        request = client.post("/post/UpdateConfig/", json = stageconfig.model_dump())
        assert request.status_code == 200

        response =  client.get("/get/CurrentConfig")
        assert response.status_code == 200
        print(C884interface.getC884Configs())
        serverstageconfig = fastapi.encoders.jsonable_encoder(response.json())
        assert fastapi.encoders.jsonable_encoder(stageconfig) == serverstageconfig

    def test_add_RS232_config_badly(self):
        """
        Same as with above, but we are adding one with RS232, i.e. without serial number. Should throw error.
        :return:
        """
        snconfig = C884RS232Config(comport = 5)
        stageconfig = StageConfig(C884 = [snconfig])
        request = client.post("/post/UpdateConfig/", json=stageconfig.model_dump())
        assert request.status_code == 500

    def test_add_connect_RS232(self):
        """
        We will try to add a controller on a nonexisting comport, comport 0.
        :return:
        """
        snconfig: C884RS232Config = C884RS232Config(comport = 0)
        request = client.post("/pi/AddRS232/", json=snconfig.model_dump())
        print(request.json())
        assert request.status_code == 500

