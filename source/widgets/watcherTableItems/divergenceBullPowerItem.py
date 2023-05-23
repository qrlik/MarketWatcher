from PySide6.QtWidgets import QTableWidgetItem

from systems import watcherController

class DivergenceBullPowerItem(QTableWidgetItem):
    def __init__(self, ticker:str):
        self.__ticker = ticker
        self.__power = 0.0
        super().__init__(str(self.__power))

    def __lt__(self, other):
        return self.__power < other.__power
    
    def update(self):
        allBullPower = 0.0
        allBearPower = 0.0
        for tf, controller in watcherController.getTicker(self.__ticker).getTimeframes().items():
            bullPower, bearPower = controller.getDivergenceController().getPowers()
            allBullPower += bullPower
            allBearPower += bearPower
        self.__power = allBullPower
        bearPercents = round(allBearPower / (allBullPower + allBearPower) * 100) if allBullPower + allBearPower > 0 else None
        super().setText(str(round(self.__power, 2)) + ' (' + str(100 - bearPercents) + ')')
