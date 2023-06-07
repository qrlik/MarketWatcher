from PySide6.QtWidgets import QFrame,QLabel,QVBoxLayout,QHBoxLayout,QTabWidget,QWidget,QAbstractItemView,QTableWidget,QTableWidgetItem,QHeaderView,QPushButton
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

from models import timeframe
from systems import cacheController
from systems import configController
from systems import watcherController

import pyperclip
import json

__widget:QFrame = None
__priceValue:QLabel = None
__tabs:QTabWidget = None
__dataButton:QPushButton = None
__tickerController = None

def setWidget(widget:QFrame):
    global __widget
    __widget = widget
    __init()

def __init():
    __initValues()
    __initTabs()

def __initValues():
    global __widget, __priceValue, __tabs, __dataButton
    __priceValue = __widget.findChild(QLabel, 'priceValue')
    __tabs = __widget.findChild(QTabWidget, 'tabWidget')
    __dataButton = __widget.findChild(QPushButton, 'copyDataButton')
    __dataButton.clicked.connect(__onDataCopyClicked)

def __initTabs():
    __tabs.tabBar().setDocumentMode(True)
    __tabs.tabBar().setExpanding(True)
    __tabs.tabBarClicked.connect(__onTabClicked)

    for tf in configController.getTimeframes():
        tabWidget = QWidget()
        tabWidget.setObjectName(tf.name)
        __tabs.addTab(tabWidget, timeframe.getPrettyFormat(tf))
        tabWidget.setLayout(QVBoxLayout())
        __initRsi(tabWidget)
        __initAtr(tabWidget)
        __initLine(tabWidget)
        __initDivergenceTable(tabWidget)
        tabWidget.layout().addStretch()

def connectTabsChanged(func):
    __tabs.tabBarClicked.connect(func)

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

def __initDivergenceTable(tab:QWidget):
    table = QTableWidget()
    table.setObjectName('divergenceTable')
    tab.layout().addWidget(table)
    table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
    table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
    table.setColumnCount(7)
    table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
    table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
    table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
    table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
    table.setHorizontalHeaderLabels(['Type', 'Power', 'Break,%', 'Break/ATR', 'Length', 'First', 'Second', ])

def __onTabClicked(index):
    if __tickerController is None:
        return
    __tabs.tabBar().setTabTextColor(index, Qt.GlobalColor.black)
    tabWidget = __tabs.widget(index)
    tf = timeframe.Timeframe[tabWidget.objectName()]
    controller = __tickerController.getTimeframe(tf).getDivergenceController()
    divergences = controller.getActuals()
    for divergence in divergences:
        time1 = divergence.firstCandle.time
        time2 = divergence.secondCandle.time
        cacheController.setDivergenceViewed(__tickerController.getTicker(), tabWidget.objectName(), time1, time2, True)
        divergence.viewed = True

def __onDataCopyClicked():
    data = {}
    data.setdefault('number')
    data.setdefault('ticker', __tickerController.getTicker() if __tickerController else None)
    data.setdefault('time')
    data.setdefault('type')
    data.setdefault('price')
    data.setdefault('stoploss')
    data.setdefault('takeprofits', [])
    data.setdefault('result')
    divers = data.setdefault('divergences', {})
    
    power = 0.0
    if __tickerController:
        for tabIndex in range(__tabs.count()):
            tabWidget = __tabs.widget(tabIndex)
            tf = timeframe.Timeframe[tabWidget.objectName()]
            controller = __tickerController.getTimeframe(tf).getDivergenceController()
            for divergence in controller.getActuals():
                power += abs(divergence.power)
                tfDivers = divers.setdefault(tabWidget.objectName(), [])
                tfDivers.append(divergence.toDict())
    data.setdefault('power', round(power))
    pyperclip.copy(str(json.dumps(data, indent = 4)))

def __updatePrice(tfController):
    lastCandle = tfController.getCandlesController().getLastCandle()
    price = lastCandle.close if lastCandle else 'null'
    __priceValue.setText(str(price))

def __updateTabValues(tabWidget:QWidget, cndlesController):
    candle = None
    candles = cndlesController.getFinishedCandles()
    if len(candles) > 0:
        candle = candles[-1]

    atrValue = tabWidget.findChild(QLabel, 'atrValue')
    atrValue.setText(str(candle.atr if candle else candle))

    rsiValue = tabWidget.findChild(QLabel, 'rsiValue')
    rsiValue.setText(str(candle.rsi if candle else candle))

def __updateDivergenceTable(tabWidget:QWidget, controller):
    table = tabWidget.findChild(QTableWidget, 'divergenceTable')
    divergences = controller.getActuals()
    divergences.sort(key = lambda info:info.power, reverse = True)
    if len(divergences) != table.rowCount():
        table.clearContents()
        table.setRowCount(len(divergences))
        for i in range(len(divergences)):
            table.setItem(i, 0, QTableWidgetItem())
            table.setItem(i, 1, QTableWidgetItem())
            table.setItem(i, 2, QTableWidgetItem())
            table.setItem(i, 3, QTableWidgetItem())
            table.setItem(i, 4, QTableWidgetItem())
            table.setItem(i, 5, QTableWidgetItem())
            table.setItem(i, 6, QTableWidgetItem())

    row = 0
    for divergence in divergences:
        color = Qt.GlobalColor.darkRed if divergence.signal.name == 'BEAR' else Qt.GlobalColor.darkGreen
        table.item(row, 0).setText(divergence.type.name)
        table.item(row, 0).setForeground(color)
        table.item(row, 1).setText(str(round(divergence.power, 2)))
        table.item(row, 2).setText(str(round(divergence.breakPercents, 2)))
        table.item(row, 3).setText(str(round(divergence.breakDelta / divergence.secondCandle.atr, 1)))
        table.item(row, 4).setText(str(divergence.secondIndex - divergence.firstIndex))
        table.item(row, 5).setText(divergence.firstCandle.time)
        table.item(row, 6).setText(divergence.secondCandle.time)
        row += 1

def __sortTabs(powerToName:list):
    powerToName.sort(key = lambda tuple:tuple[0], reverse = True)
    for sortIndex in range(len(powerToName)):
        _, name = powerToName[sortIndex]
        for tabIndex in range(__tabs.count()):
            if __tabs.widget(tabIndex).objectName() == name:
                __tabs.tabBar().moveTab(tabIndex, sortIndex)

def __updateVisible():
    for tabIndex in range(__tabs.count()):
        tabWidget = __tabs.widget(tabIndex)
        tf = timeframe.Timeframe[tabWidget.objectName()]
        tfController = __tickerController.getTimeframe(tf)
        __tabs.setTabVisible(tabIndex, not tfController.getDivergenceController().isEmpty())

def update(ticker:str, byClick):
    global __tickerController
    __tickerController = watcherController.getTicker(ticker + 'USDT')

    powerToName = []
    for tabIndex in range(__tabs.count()):
        tabWidget = __tabs.widget(tabIndex)
        tf = timeframe.Timeframe[tabWidget.objectName()]
        tfController = __tickerController.getTimeframe(tf)

        if tabIndex == 0:
            __updatePrice(tfController)
        __tabs.setTabVisible(tabIndex, True)
        __updateTabValues(tabWidget, tfController.getCandlesController())
        __updateDivergenceTable(tabWidget, tfController.getDivergenceController())
        powers = tfController.getDivergenceController().getPowers()
        powerToName.append((powers.bullPower + abs(powers.bearPower), tf.name))
        color = QColor(255,102,0,255) if powers.newBullPower > 0 or powers.newBearPower > 0 else Qt.GlobalColor.black
        __tabs.tabBar().setTabTextColor(tabIndex, color)

    __sortTabs(powerToName)
    __updateVisible()
    if byClick:
        __tabs.setCurrentIndex(0)

            