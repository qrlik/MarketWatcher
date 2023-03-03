from PySide6.QtWidgets import QFrame,QLabel

from systems import watcherController

__widget:QFrame = None
__priceValue:QLabel = None

def setWidget(widget:QFrame):
    global __widget, __priceValue
    __widget = widget
    __priceValue = __widget.findChild(QLabel, 'priceValue')

def update(ticker:str):
    tickerController = watcherController.getTicker(ticker)
    timeframes = tickerController.getTimeframes()
    first = True

    for timeframe, controller in timeframes.items():
        if first:
            first = False
            price = controller.getCurrentCandle().close
            __priceValue.setText(str(price))