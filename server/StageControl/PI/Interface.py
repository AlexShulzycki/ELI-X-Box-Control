import asyncio
from typing import Any

from server.StageControl.DataTypes import ControllerInterface, StageStatus, StageInfo
from server.StageControl.PI.DataTypes import PISettings, PIControllerStatus


def deconstruct_SN_Channel(sn_channel):
    """
    Extracts the channel and serial number from a unique serial-number-channel identifier
    :param sn_channel: serial number with the channel glued to the end
    :return: serial number and channel, separately!
    """
    channel: int = sn_channel % 10  # modulo 10 gives last digit
    sn: int = int((sn_channel - channel) / 10)  # minus channel, divide by 10 to get rid of 0
    return sn, channel

class PIControllerInterface(ControllerInterface):

    def __init__(self):
        super().__init__()
        self.settings = PISettings()
        """The PISettings is handling basically everything for us"""

    @property
    def stages(self) -> list[int]:
        pass

    def moveTo(self, identifier: int, position: float):
        sn, channel = deconstruct_SN_Channel(identifier)
        self.settings.controllers[sn].moveTo(channel, position)

    @property
    def stageInfo(self) -> dict[int, StageInfo]:
        return self.settings.stageInfo

    def getAllControllerSNs(self) -> list[int]:
        sns: list[int] = []
        for cntrl in self.settings.controllers.keys():
            sns.append(cntrl)
        return sns

    def getRelevantControllerSNs(self, identifiers: list[int] = None) -> list[int]:
        # tease out the serial number of the relevant controllers
        controller_sn: list[int] = []
        if identifiers is None:
            # grab all serial numbers if none
            controller_sn = self.getAllControllerSNs()
        else:
            for idnt in identifiers:
                sn, channel = deconstruct_SN_Channel(idnt)
                if not controller_sn.__contains__(sn):
                    controller_sn.append(sn)
        return controller_sn

    async def updateStageInfo(self, identifiers: list[int] = None):
        """
        Do a full refresh of each controller's status.
        :param identifiers: identifiers of stages we want to update
        """
        controller_sn = self.getRelevantControllerSNs(identifiers)

        # run it async and call it a day
        awaiters = []
        for sn in controller_sn:
            awaiters.append(self.settings.controllers[sn].refreshFullStatus())
        await asyncio.gather(*awaiters)

        super().updateStageInfo()

    @property
    def stageStatus(self) -> dict[int, StageStatus]:
        return self.settings.stageStatus

    async def updateStageStatus(self, identifiers: list[int] = None):
        """
        Refresh position and ontarget of the given identifiers' controllers.
        :param identifiers: SN-Channel combo identifier
        :return:
        """
        controller_sn = self.getRelevantControllerSNs(identifiers)

        # run it async and call it a day
        awaiters = []
        for sn in controller_sn:
            awaiters.append(self.settings.controllers[sn].refreshPosOnTarget())
        await asyncio.gather(*awaiters)

        super().updateStageStatus()
        pass
