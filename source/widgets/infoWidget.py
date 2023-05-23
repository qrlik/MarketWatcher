from PySide6.QtWidgets import QFrame,QLabel,QVBoxLayout,QHBoxLayout,QTabWidget,QWidget,QListWidget,QAbstractItemView,QListWidgetItem

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
        tabWidget.setObjectName(tf.name + '_tab')
        __tabs.addTab(tabWidget, timeframe.getPrettyFormat(tf))
        tabWidget.setLayout(QVBoxLayout())
        __initRsi(tabWidget)
        __initAtr(tabWidget)
        __initLine(tabWidget)
        __initDivergenceList(tabWidget)
        tabWidget.layout().addStretch()

def __initRsi(tab:QWidget):
    layout = QHBoxLayout()
    layout.setObjectName('rsiLayout')
    tab.layout().addLayout(layout)

    rsiLabel = QLabel('Rsi')
    rsiLabel.setObjectName('rsiLabel')
    layout.addWidget(rsiLabel)
    layout.addStretch()

    rsiValue = QLabel('0.0')
    rsiValue.setObjectName('rsiValue')
    layout.addWidget(rsiValue)

def __initAtr(tab:QWidget):
    layout = QHBoxLayout()
    layout.setObjectName('atrLayout')
    tab.layout().addLayout(layout)

    atrLabel = QLabel('Atr')
    atrLabel.setObjectName('atrLabel')
    layout.addWidget(atrLabel)
    layout.addStretch()

    atrValue = QLabel('0.0')
    atrValue.setObjectName('atrValue')
    layout.addWidget(atrValue)

def __initLine(tab:QWidget):
    line = QFrame()
    line.setObjectName('line')
    tab.layout().addWidget(line)
    line.setFrameShadow(QFrame.Shadow.Sunken)
    line.setFrameShape(QFrame.Shape.HLine)

def __initDivergenceList(tab:QWidget):
    list = QListWidget()
    list.setObjectName('divergenceList')
    tab.layout().addWidget(list)
    list.itemSelectionChanged.connect(__showDivergenceTip)
    list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

def __showDivergenceTip():
    pass

def __updateDivergenceList(list:QListWidget, controller):
    divergences = controller.getActuals()
    divergences.sort(key = lambda info:info.power, reverse = True)
    insert = False
    if len(divergences) != list.count():
        insert = True
        list.clear()
    i = 0
    for divergence in divergences:
        text = divergence.type.name + '\t' + str(round(divergence.power, 2))
        if insert:
            list.insertItem(0, QListWidgetItem(text))
        else:
            list.item(i).setText(text)
        i += 1

def update(ticker:str):
    tickerController = watcherController.getTicker(ticker)
    timeframes = tickerController.getTimeframes()
    first = True

    index = 0
    for _, controller in timeframes.items():
        if first:
            first = False
            lastCandle = controller.getCandlesController().getLastCandle()
            price = lastCandle.close if lastCandle else 'null'
            __priceValue.setText(str(price))

        tabWidget = __tabs.widget(index)
        index += 1
        candle = None
        candles = controller.getCandlesController().getFinishedCandles()
        if len(candles) > 0:
            candle = candles[-1]

        atrValue = tabWidget.findChild(QLabel, 'atrValue')
        atrValue.setText(str(candle.atr if candle else candle))

        rsiValue = tabWidget.findChild(QLabel, 'rsiValue')
        rsiValue.setText(str(candle.rsi if candle else candle))

        divergenceList = tabWidget.findChild(QListWidget, 'divergenceList')
        __updateDivergenceList(divergenceList, controller.getDivergenceController())