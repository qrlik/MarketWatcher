
from PySide6.QtWidgets import QTableWidgetItem

from systems import watcherController

class DivergenceBearPowerItem(QTableWidgetItem):
    def __init__(self, ticker:str):
        self.__ticker = ticker
        super().__init__(str(0))

    def update(self):
        allBullPower = 0.0
        allBearPower = 0.0
        for _, controller in watcherController.getTicker(self.__ticker).getTimeframes().items():
            powers = controller.getDivergenceController().getPowers()
            allBullPower += powers.bullPower
            allBearPower += powers.bearPower
        bearPercents = round(allBearPower / (allBullPower + allBearPower) * 100) if allBullPower + allBearPower > 0 else None
        super().setText(str(bearPercents))

