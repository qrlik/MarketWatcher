
from PySide6.QtWidgets import QListWidgetItem
from systems import watcherController

class ListTicketItem(QListWidgetItem):
    def __init__(self, ticker:str):
        self.__ticker = ticker
        super().__init__(ticker)

    def __lt__(self, other):
        return super().text() < other.text()
    
    def update(self):
        newText = self.__ticker + '\t'
        for timeframe, controller in reversed(watcherController.getTicker(self.__ticker).getTimeframes().items()):
            signals = controller.getSignalController().getSignals()
            if len(signals) > 0:
                newText += timeframe + '('
            for signal in signals:
                newText += signal.name + ','
            newText = newText[:-1] + ') '
        super().setText(newText)

    __ticker:str = ''
