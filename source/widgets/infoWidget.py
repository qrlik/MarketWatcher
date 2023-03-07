from PySide6.QtWidgets import QFrame,QLabel,QVBoxLayout,QHBoxLayout,QSpacerItem

from models import movingAverage
from systems import configController
from systems import watcherController

__widget:QFrame = None
__priceValue:QLabel = None
__deltas = {}
__averages = {}

def setWidget(widget:QFrame):
    global __widget, __priceValue
    __widget = widget
    __priceValue = __widget.findChild(QLabel, 'priceValue')
    __init()

def __init():
    __initDeltas()
    __initAverages()

def __initDeltas():
    layout:QVBoxLayout = __widget.findChild(QVBoxLayout, 'deltasLayout')
    for timeframe in configController.getConfigs():
        newLayout = QHBoxLayout()
        newLayout.setObjectName(timeframe + '_deltaLayout')
        layout.addLayout(newLayout)

        deltaLabel = QLabel(timeframe)
        deltaLabel.setObjectName(timeframe + '_deltaLabel')
        newLayout.addWidget(deltaLabel)
        newLayout.addStretch()

        deltaValue = QLabel('0.0')
        deltaValue.setObjectName(timeframe + '_deltaValue')
        newLayout.addWidget(deltaValue)

def __initAverages():
    layout:QVBoxLayout = __widget.findChild(QVBoxLayout, 'averagesLayout')
    for average in movingAverage.MovingAverageType:
        newLayout = QHBoxLayout()
        newLayout.setObjectName(average.name + '_averageLayout')
        layout.addLayout(newLayout)

        averageLabel = QLabel(average.name)
        averageLabel.setObjectName(average.name + '_averageLabel')
        newLayout.addWidget(averageLabel)
        newLayout.addStretch()

        averageValue = QLabel('0.0')
        averageValue.setObjectName(average.name + '_averageValue')
        newLayout.addWidget(averageValue)

def update(ticker:str):
    tickerController = watcherController.getTicker(ticker)
    timeframes = tickerController.getTimeframes()
    first = True

    for timeframe, controller in timeframes.items():
        if first:
            first = False
            price = controller.getCurrentCandle().close
            __priceValue.setText(str(price))

        deltaValue = __widget.findChild(QLabel, timeframe + '_deltaValue')
        deltaValue.setText(str(controller.getDeltaController().getPrettyDelta()))

    for average in movingAverage.MovingAverageType:
        averageValue = __widget.findChild(QLabel, average.name + '_averageValue')
        average = controller.getAveragesController().getAverage(average)
        averageText = str(average) if average else '0.0'
        averageValue.setText(averageText)