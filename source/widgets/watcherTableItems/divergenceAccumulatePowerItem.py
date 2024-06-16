
from PySide6.QtWidgets import QTableWidgetItem
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

from systems import watcherController
from systems import userDataController
from utilities import guiDefines

class DivergenceAccumulatePowerItem(QTableWidgetItem):
    def __init__(self, ticker:str):
        self.__ticker = ticker
        self.__power = 0.0
        super().__init__(str(self.__power))

    def __lt__(self, other):
        return self.getSortPower() < other.getSortPower()
    
    def getSortPower(self):
        data = userDataController.getTickerUserData(self.__ticker)
        if data.isOpened():
            return data.getLastUpdate()
        return self.__power

    def getTicker(self):
        return self.__ticker

    def update(self):
        self.__power = -1.0
        super().setText('')

        tickerController = watcherController.getTicker(self.__ticker)
        if not tickerController.isValidLastCandle():
            return
    
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
        
        if self.__power > 0.0:
            text = str(round(self.__power, 2)) + ' (' + str(round(allPower, 2)) + ')'
            super().setText(text)
        else:
            super().setText('')

        super().setForeground(guiDefines.defaultFontColor if allNewPower == 0.0 else guiDefines.notViewedColor)
