from PySide6.QtWidgets import QFrame,QLabel,QVBoxLayout,QHBoxLayout,QTabWidget,QWidget,QAbstractItemView,QTableWidget,QTableWidgetItem,QHeaderView
from PySide6.QtCore import Qt

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
    __tabs.tabBar().setDocumentMode(True)
    __tabs.tabBar().setExpanding(True)
    __init()

def __init():
    __initTabs()

def __initTabs():
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
        table.item(row, 2).setText(str(round(divergence.breakDelta / divergence.secondCandle.close * 100, 2)))
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

def __updateVisible(tickerController):
    for tabIndex in range(__tabs.count()):
        tabWidget = __tabs.widget(tabIndex)
        tf = timeframe.Timeframe[tabWidget.objectName()]
        tfController = tickerController.getTimeframe(tf)
        __tabs.setTabVisible(tabIndex, not tfController.getDivergenceController().isEmpty())

def update(ticker:str, byClick):
    tickerController = watcherController.getTicker(ticker)

    powerToName = []
    for tabIndex in range(__tabs.count()):
        tabWidget = __tabs.widget(tabIndex)
        tf = timeframe.Timeframe[tabWidget.objectName()]
        tfController = tickerController.getTimeframe(tf)

        if tabIndex == 0:
            __updatePrice(tfController)
        __tabs.setTabVisible(tabIndex, True)
        __updateTabValues(tabWidget, tfController.getCandlesController())
        __updateDivergenceTable(tabWidget, tfController.getDivergenceController())
        bullPower, bearPower = tfController.getDivergenceController().getPowers()
        powerToName.append((abs(bullPower - bearPower), tf.name))
    __sortTabs(powerToName)
    __updateVisible(tickerController)
    if byClick:
        __tabs.setCurrentIndex(0)
            