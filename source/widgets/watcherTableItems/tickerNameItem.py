
from PySide6.QtWidgets import QTableWidgetItem

from systems import userDataController

class TickerNameItem(QTableWidgetItem):
    def __init__(self, ticker:str):
        self.__ticker = ticker
        super().__init__(ticker[:-4] if ticker.endswith('USDT') else ticker)

    def __lt__(self, other):
        return self.__ticker < other.__ticker
    
    def getTicker(self):
        return self.__ticker

    def update(self):
        super().setForeground(userDataController.getTickerUserData(self.__ticker).getPositionColor())
