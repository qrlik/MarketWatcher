
from PySide6.QtWidgets import QTableWidgetItem

from systems import watcherController
from systems import userDataController
from utilities import guiDefines

class ChannelPowerItem(QTableWidgetItem):
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

    def update(self):
        self.__power = -1.0
        super().setText('')

        tickerController = watcherController.getTicker(self.__ticker)
        if not tickerController.isValidLastCandle():
            return
    
        relevance = False
        maxPower = 0.0
        allPower = 0.0
        allNewPower = 0.0
        for _, controller in watcherController.getTicker(self.__ticker).getFilteredTimeframes().items():
            powers = controller.getChannelController().getPowers()
            if powers.relevancePower > 0.0 and not relevance:
                relevance = True
                maxPower = 0.0
                allPower = 0.0
                allNewPower = 0.0

            allNewPower += powers.newRelevancePower if relevance else powers.newPower
            allPower += powers.relevancePower if relevance else powers.power
            maxPower = max(maxPower, powers.maxRelevancePower) if relevance else max(maxPower, powers.maxPower)

        self.__relevance = relevance
        self.__power = maxPower
        
        if self.__power > 0.0:
            text = str(round(self.__power, 2)) + ' (' + str(round(allPower, 2)) + ')'
            super().setText(text)
        else:
            super().setText('')

        if allNewPower > 0.0:
            super().setForeground(guiDefines.notViewedColor)
        elif self.__relevance:
            super().setForeground(guiDefines.defaultFontColor)
        else:
            super().setForeground(guiDefines.zeroColor)
