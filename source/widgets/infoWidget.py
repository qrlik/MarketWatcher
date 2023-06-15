from PySide6.QtWidgets import QFrame,QLabel,QVBoxLayout,QHBoxLayout,QTabWidget,QWidget,QAbstractItemView,QTableWidget,QTableWidgetItem,QHeaderView,QPushButton,QProgressBar
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

from models import timeframe
from systems import cacheController
from systems import configController
from systems import watcherController
from utilities import guiDefines

import pyperclip
import json

__widget:QFrame = None
__priceValue:QLabel = None
__tabs:QTabWidget = None
__dataButton:QPushButton = None
__divergenceRatio:QProgressBar = None
__tickerController = None

def setWidget(widget:QFrame):
    global __widget
    __widget = widget
    __init()

def __init():
    __initValues()
    __initProgressBar()
    __initTabs()

def __initValues():
    global __widget, __priceValue, __tabs, __dataButton,__divergenceRatio
    __priceValue = __widget.findChild(QLabel, 'priceValue')
    __tabs = __widget.findChild(QTabWidget, 'tabWidget')
    __divergenceRatio = __widget.findChild(QProgressBar, 'divergenceRatio')
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

def __initProgressBar():
    global __divergenceRatio
    __divergenceRatio.setStyleSheet(guiDefines.getEmptyProgressBarSheed())

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
    
    heads = ['Type', 'Power', 'Break,%', 'Break/ATR', 'Length', 'First', 'Second' ]
    table.setColumnCount(len(heads))
    for i in range(len(heads)):
        table.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)
    table.setHorizontalHeaderLabels(heads)

def __onTabClicked(index):
    if __tickerController is None:
        return
    __tabs.tabBar().setTabTextColor(index, guiDefines.defaultColor)
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

def __updatePrice():
    price = None
    if __tickerController:
        for _, controller in __tickerController.getTimeframes().items():
            lastCandle = controller.getCandlesController().getLastCandle()
            price = lastCandle.close if lastCandle else None
            break
    __priceValue.setText(str(price))

def __updateProgressBar():
    if __tickerController is None:
        return
    global __divergenceRatio
    allBullPower = 0.0
    allBearPower = 0.0
    for _, controller in __tickerController.getTimeframes().items():
        powers = controller.getDivergenceController().getPowers()
        allBullPower += powers.bullPower
        allBearPower += powers.bearPower
    summary = allBullPower + allBearPower
    isEnabled = allBullPower + allBearPower > 0.0
    if isEnabled:
        __divergenceRatio.setStyleSheet(guiDefines.getDefaultProgressBarSheet())
        __divergenceRatio.setValue(round(allBullPower / (summary) * 100))
    else:
        __divergenceRatio.setStyleSheet(guiDefines.getEmptyProgressBarSheed())
        __divergenceRatio.setValue(0)

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
        for row in range(len(divergences)):
            for column in range(7):
                item = QTableWidgetItem()
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                table.setItem(row, column, item)

    row = 0
    for divergence in divergences:
        color = guiDefines.bearColor if divergence.signal.name == 'BEAR' else guiDefines.bullColor
        table.item(row, 0).setText(divergence.type.name)
        table.item(row, 0).setForeground(color)
        table.item(row, 1).setText(str(round(divergence.power, 2)))
        table.item(row, 2).setText(str(round(divergence.breakPercents, 2)))
        table.item(row, 3).setText(str(round(divergence.breakDelta / divergence.secondCandle.atr, 1)))
        table.item(row, 4).setText(str(divergence.secondIndex - divergence.firstIndex))
        table.item(row, 5).setText(divergence.firstCandle.time[:-5])
        table.item(row, 6).setText(divergence.secondCandle.time[:-5])
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
    __tickerController = watcherController.getTicker(ticker)

    powerToName = []
    __updateProgressBar()
    __updatePrice()
    for tabIndex in range(__tabs.count()):
        tabWidget = __tabs.widget(tabIndex)
        tf = timeframe.Timeframe[tabWidget.objectName()]
        tfController = __tickerController.getTimeframe(tf)

        __tabs.setTabVisible(tabIndex, True)
        __updateTabValues(tabWidget, tfController.getCandlesController())
        __updateDivergenceTable(tabWidget, tfController.getDivergenceController())
        powers = tfController.getDivergenceController().getPowers()
        powerToName.append((powers.bullPower + abs(powers.bearPower), tf.name))
        color = QColor(255,102,0,255) if powers.newBullPower > 0 or powers.newBearPower > 0 else Qt.GlobalColor.white
        __tabs.tabBar().setTabTextColor(tabIndex, color)

    __sortTabs(powerToName)
    __updateVisible()
    if byClick:
        __tabs.setCurrentIndex(0)

            