
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
        if tickerController.isInvalidLastCandle():
            super().setForeground(guiDefines.invalidLastCandleColor)
            return
        if not tickerController.isValidVolume():
            super().setForeground(guiDefines.invalidVolumeColor)
            return
        if tickerController.isDirtyLastCandle():
            super().setForeground(guiDefines.dirtyLastCandleColor)
            return
        
        positionColor = userDataController.getTickerUserData(self.__ticker).getPositionColor()
        super().setForeground(positionColor)
        if positionColor != guiDefines.defaultFontColor:
            return
        
        if tickerController.isBored():
            super().setForeground(guiDefines.boredColor)
