
from PySide6.QtWidgets import QTableWidgetItem

from systems import watcherController
from systems import userDataController
from utilities import guiDefines

class PowerItem(QTableWidgetItem):
    def __init__(self, ticker:str):
        self.__ticker = ticker
        self.__power = 0.0
        self.__relevance = False
        super().__init__(str(self.__power))

    def __lt__(self, other):
        return self.getSortPower() < other.getSortPower()
    
    def getSortPower(self):
        if self.__relevance:
            return self.__power + 1_000_000
        return self.__power

    def getTicker(self):
        return self.__ticker

    def __updateChannelRelevance(self):
        for _, controller in watcherController.getTicker(self.__ticker).getFilteredTimeframes().items():
            powers = controller.getChannelController().getPowers()
            if powers.relevancePower > 0.0:
                self.__relevance = True
                return

    def __updateDivergencePower(self):
        maxPower = 0.0
        allPower = 0.0
        allNewPower = 0.0
        for _, controller in watcherController.getTicker(self.__ticker).getFilteredTimeframes().items():
            powers = controller.getDivergenceController().getRegularPowers()

            if powers.bullPower <= 0.0 and powers.bearPower <= 0.0: # tf filter && logic
                allPower = 0.0
                break
            
            allNewPower += powers.newBullPower
            allNewPower += abs(powers.newBearPower)

            allPower += powers.bullPower
            allPower += abs(powers.bearPower)

            maxPower = max(maxPower, powers.maxPower)

        self.__power = maxPower
        return allNewPower > 0.0

    def update(self):
        self.__power = -10.0
        super().setText('')

        tickerController = watcherController.getTicker(self.__ticker)
        if not tickerController.isValidLastCandle():
            self.__power = -9.0
            return
        if not tickerController.isValidVolume():
            self.__power = -8.0
            return
    
        self.__updateChannelRelevance()
        haveNewPowers = False
        if self.__relevance:
            haveNewPowers = self.__updateDivergencePower()

        if self.__power > 0.0:
            text = str(round(self.__power, 2))
            super().setText(text)
        else:
            super().setText('')

        if self.__relevance:
            if haveNewPowers:
                super().setForeground(guiDefines.notViewedColor)
            else:
                super().setForeground(guiDefines.defaultFontColor)
        else:
            super().setForeground(guiDefines.zeroColor)
