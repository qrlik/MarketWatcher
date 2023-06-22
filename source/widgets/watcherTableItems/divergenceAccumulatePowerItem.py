
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
        for _, controller in watcherController.getTicker(self.__ticker).getFilteredTimeframes().items():
            powers = controller.getDivergenceController().getPowers()
            allPower += powers.bullPower
            allPower += abs(powers.bearPower)

        self.__power = allPower
        super().setText(str(int(self.__power)))
