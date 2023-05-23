from PySide6.QtWidgets import QFrame,QLabel,QVBoxLayout,QHBoxLayout,QTabWidget,QWidget,QAbstractItemView,QTableWidget,QTableWidgetItem,QHeaderView

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
        tabWidget.setObjectName(tf.name + '_tab')
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
    table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
    table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)
    table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeMode.Stretch)
    table.setHorizontalHeaderLabels(['Type', 'Power', 'First', 'Second', 'Length', 'Break,%', 'Break/ATR'])

def __updateDivergenceTable(table:QTableWidget, controller):
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
        table.item(row, 0).setText(divergence.type.name)
        table.item(row, 1).setText(str(round(divergence.power, 2)))
        table.item(row, 2).setText(divergence.firstCandle.time)
        table.item(row, 3).setText(divergence.secondCandle.time)
        table.item(row, 4).setText(str(divergence.secondIndex - divergence.firstIndex))
        table.item(row, 5).setText(str(round(divergence.breakDelta / divergence.secondCandle.close * 100, 2)))
        table.item(row, 6).setText(str(round(divergence.breakDelta / divergence.secondCandle.atr, 1)))
        # to do may be change to current candle? or think about dynamic power
        row += 1

def update(ticker:str):
    tickerController = watcherController.getTicker(ticker)
    timeframes = tickerController.getTimeframes()
    first = True

    index = -1
    for _, controller in timeframes.items():
        index += 1
        if first:
            first = False
            lastCandle = controller.getCandlesController().getLastCandle()
            price = lastCandle.close if lastCandle else 'null'
            __priceValue.setText(str(price))

        tabWidget = __tabs.widget(index)
        
        candle = None
        candles = controller.getCandlesController().getFinishedCandles()
        if len(candles) > 0:
            candle = candles[-1]

        atrValue = tabWidget.findChild(QLabel, 'atrValue')
        atrValue.setText(str(candle.atr if candle else candle))

        rsiValue = tabWidget.findChild(QLabel, 'rsiValue')
        rsiValue.setText(str(candle.rsi if candle else candle))

        divergenceTable = tabWidget.findChild(QTableWidget, 'divergenceTable')
        __updateDivergenceTable(divergenceTable, controller.getDivergenceController())
        __tabs.setTabVisible(index, not controller.getDivergenceController().isEmpty())
            