
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
        allPower = 0.0
        allNewPower = 0.0
        for _, controller in watcherController.getTicker(self.__ticker).getTimeframes().items():
            powers = controller.getDivergenceController().getPowers()
            allPower += powers.bullPower
            allNewPower += powers.newBullPower
            allPower += abs(powers.bearPower)
            allNewPower += abs(powers.newBearPower)

        self.__power = allPower
        if allNewPower > 1:
            super().setForeground(QColor(255,102,0,255))
            super().setText(str(int(self.__power)) + ' (' + str(int(allNewPower)) + ')');
        else:
            super().setForeground(guiDefines.defaultColor)
            super().setText(str(int(self.__power)))
