from PySide6.QtWidgets import QFrame,QLabel,QVBoxLayout,QHBoxLayout,QTabWidget,QWidget

from models import timeframe
from systems import configController
from systems import watcherController

__widget:QFrame = None
__priceValue:QLabel = None
__tabs:QTabWidget = None

def setWidget(widget:QFrame):
    global __widget, __priceValue, __tabs
    __widget = widget
    __priceValue = __widget.findChild(QLabel, 'priceValue')
    __tabs = __widget.findChild(QTabWidget, 'tabWidget')
    __init()

def __init():
    __initTabs()

def __initTabs():
    for tf in configController.getTimeframes():
        tabWidget = QWidget()
        tabWidget.setObjectName(tf + '_tab')
        __tabs.addTab(tabWidget, timeframe.getPrettyFormat(tf))
        tabWidget.setLayout(QVBoxLayout())
        __initDeltas(tabWidget)
        __initLine(tabWidget)
        __initAverages(tabWidget, tf)
        tabWidget.layout().addStretch()

def __initDeltas(tab:QWidget):
    layout = QHBoxLayout()
    layout.setObjectName('deltaLayout')
    tab.layout().addLayout(layout)

    deltaLabel = QLabel('Delta, %')
    deltaLabel.setObjectName('deltaLabel')
    layout.addWidget(deltaLabel)
    layout.addStretch()

    deltaValue = QLabel('0.0')
    deltaValue.setObjectName('deltaValue')
    layout.addWidget(deltaValue)

def __initLine(tab:QWidget):
    line = QFrame()
    line.setObjectName('line')
    tab.layout().addWidget(line)
    line.setFrameShadow(QFrame.Shadow.Sunken)
    line.setFrameShape(QFrame.Shape.HLine)

def __initAverages(tab:QWidget, timeframe:str):
    layout = QVBoxLayout()
    layout.setObjectName('averagesLayout')
    tab.layout().addLayout(layout)
    for average in configController.getTimeframeAverages(timeframe):
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

    index = 0
    for _, controller in timeframes.items():
        if first:
            first = False
            price = controller.getCurrentCandle().close
            __priceValue.setText(str(price))

        tabWidget = __tabs.widget(index)
        index += 1
        deltaValue = tabWidget.findChild(QLabel, 'deltaValue')
        deltaValue.setText(str(controller.getAtrController().getAtr()))

        for average, value in controller.getAveragesController().getAverages().items():
            averageValue = tabWidget.findChild(QLabel, average.name + '_averageValue')
            averageText = str(round(value, tickerController.getPricePrecision())) if value else '0.0'
            averageValue.setText(averageText)