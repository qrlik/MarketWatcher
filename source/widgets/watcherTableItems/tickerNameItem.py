
from PySide6.QtWidgets import QTableWidgetItem

from systems import watcherController
from systems import userDataController
from utilities import guiDefines

class TickerNameItem(QTableWidgetItem):
    def __init__(self, ticker:str):
        self.__ticker = ticker
        super().__init__(ticker[:-4] if ticker.endswith('USDT') else ticker)

    def __lt__(self, other):
        return self.__ticker < other.__ticker
    
    def getTicker(self):
        return self.__ticker

    def update(self):
        positionColor = userDataController.getTickerUserData(self.__ticker).getPositionColor()
        super().setForeground(positionColor)
        if positionColor == guiDefines.defaultFontColor:
            allPower = 0.0
            for _, controller in watcherController.getTicker(self.__ticker).getFilteredTimeframes().items():
                powers = controller.getDivergenceController().getRegularPowers()
                allPower += powers.bullPower
                allPower += abs(powers.bearPower)

            if allPower == 0.0:
                super().setForeground(guiDefines.zeroColor)
