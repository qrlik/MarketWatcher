from PySide6.QtWidgets import QFrame,QLabel,QVBoxLayout,QHBoxLayout,QTabWidget,QWidget

from models import movingAverage
from systems import configController
from systems import watcherController

__widget:QFrame = None
__priceValue:QLabel = None
__tabs:QTabWidget = None
__deltas = {}
__averages = {}

def setWidget(widget:QFrame):
    global __widget, __priceValue, __tabs
    __widget = widget
    __priceValue = __widget.findChild(QLabel, 'priceValue')
    __tabs = __widget.findChild(QTabWidget, 'tabWidget')
    __init()

def __init():
    __initTabs()

def __initTabs():
    for timeframe in configController.getConfigs():
        tabWidget = QWidget()
        __tabs.addTab(tabWidget, timeframe)
        tabWidget.setObjectName(timeframe + '_tab')
        tabWidget.setLayout(QVBoxLayout())
        __initDeltas(tabWidget)
        __initLine(tabWidget)
        __initAverages(tabWidget)

def __initDeltas(tab:QWidget):
    layout = QVBoxLayout()
    layout.setObjectName('deltasLayout')
    tab.layout().addLayout(layout)
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

def __initLine(tab:QWidget):
    line = QFrame()
    line.setObjectName('line')
    tab.layout().addWidget(line)
    line.setFrameShadow(QFrame.Shadow.Sunken)
    line.setFrameShape(QFrame.Shape.HLine)

def __initAverages(tab:QWidget):
    layout = QVBoxLayout()
    layout.setObjectName('averagesLayout')
    tab.layout().addLayout(layout)
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