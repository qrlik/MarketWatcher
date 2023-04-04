
from PySide6.QtWidgets import QListWidgetItem

from models import timeframe
from systems import watcherController

class ListTicketItem(QListWidgetItem):
    def __init__(self, ticker:str):
        self.__ticker = ticker
        super().__init__(ticker)

    def __lt__(self, other):
        return super().text() < other.text()
    
    def getTicker(self):
        return self.__ticker

    def update(self):
        newText = self.__ticker + '\t'
        for tf, controller in reversed(watcherController.getTicker(self.__ticker).getTimeframes().items()):
            signals = controller.getSignalController().getSignals()
            if len(signals) > 0:
                newText += timeframe.getPrettyFormat(tf) + '('
                for signal in signals:
                    newText += signal[0].name + ','
                newText = newText[:-1] + ') '
        super().setText(newText)
