
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
        tickerController = watcherController.getTicker(self.__ticker)
        if not tickerController.isValidLastCandle():
            super().setForeground(guiDefines.invalidLastCandleColor)
            return
        if not tickerController.isFeeAcceptable():
            super().setForeground(guiDefines.unacceptableFeeColor)
            return
        
        positionColor = userDataController.getTickerUserData(self.__ticker).getPositionColor()
        super().setForeground(positionColor)
        if positionColor != guiDefines.defaultFontColor:
            return
        
        allPower = 0.0
        for _, controller in tickerController.getFilteredTimeframes().items():
            powers = controller.getDivergenceController().getRegularPowers()
            if powers.bullPower == 0.0 and powers.bearPower == 0.0:
                allPower = 0.0
                break
            
            allPower += powers.bullPower
            allPower += abs(powers.bearPower)


        if allPower == 0.0:
            super().setForeground(guiDefines.zeroColor)
