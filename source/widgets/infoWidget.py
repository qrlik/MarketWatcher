from PySide6.QtWidgets import QFrame,QLabel,QVBoxLayout,QHBoxLayout,QTabWidget,QWidget,QAbstractItemView,QTableWidget,QTableWidgetItem,QHeaderView,QPushButton,QProgressBar
from PySide6.QtCore import Qt

from models import timeframe
from systems import configController
from systems import userDataController
from systems import watcherController
from utilities import guiDefines
from widgets.filters import timeframesFilter

import pyperclip
import json
import webbrowser

__widget:QFrame = None
__priceValue:QLabel = None
__tabs:QTabWidget = None
__table:QTableWidget = None
__dataButton:QPushButton = None
__linkButton:QPushButton = None
__divergenceRatio:QProgressBar = None
__tickerController = None
__url = 'https://www.tradingview.com/chart/?symbol=BINANCE:'

def init(parent):
    global __widget
    __widget = parent.findChild(QFrame, 'infoWidget')
    __widget.setFixedWidth(500)
    __init()

def __init():
    __initValues()
    __initButtons()
    __initProgressBar()
    __initTabs()
    __initDivergenceTable()

def __initValues():
    global __widget, __priceValue, __tabs, __dataButton,__divergenceRatio,__linkButton,__table
    __priceValue = __widget.findChild(QLabel, 'priceValue')
    __tabs = __widget.findChild(QTabWidget, 'tabWidget')
    __table = __widget.findChild(QTableWidget, 'tableWidget')
    __divergenceRatio = __widget.findChild(QProgressBar, 'divergenceRatio')
    __dataButton = __widget.findChild(QPushButton, 'copyDataButton')
    __linkButton = __widget.findChild(QPushButton, 'openLinkButton')

def __initButtons():
    __dataButton.clicked.connect(__onDataCopyClicked)

    __linkButton.setText('Spot')
    __linkButton.clicked.connect(__onOpenSpotLinkClicked)

    layout = __widget.findChild(QHBoxLayout, 'positionLayout')
    futureButton = QPushButton('Future')
    layout.addWidget(futureButton)
    futureButton.clicked.connect(__onOpenFutureLinkClicked)

def __initTabs():
    __tabs.tabBar().setDocumentMode(True)
    __tabs.tabBar().setExpanding(True)

    for tf in configController.getTimeframes():
        tabWidget = QWidget()
        tabWidget.setObjectName(tf.name)
        __tabs.addTab(tabWidget, timeframe.getPrettyFormat(tf))
        tabWidget.setLayout(QVBoxLayout())
        __initRsi(tabWidget)
        __initAtr(tabWidget)
        tabWidget.layout().addStretch()

def __initProgressBar():
    global __divergenceRatio
    __divergenceRatio.setStyleSheet(guiDefines.getEmptyProgressBarSheet())

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

def __initDivergenceTable():
    global __table
    __table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
    __table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
    
    heads = ['Type', 'Power', 'Break,%', 'Length', 'From' ]
    __table.setColumnCount(len(heads))
    for i in range(len(heads)):
        __table.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)
    __table.setHorizontalHeaderLabels(heads)

def __onDataCopyClicked():
    ticker = __tickerController.getTicker() if __tickerController else ''
    data = {}
    data.setdefault('number')
    data.setdefault('ticker', ticker)
    data.update(userDataController.getTickerJsonData(ticker))
    data.setdefault('stoploss')
    data.setdefault('takeprofits', [])
    data.setdefault('result')
    divers = data.setdefault('divergences', {})
    
    power = 0.0
    if __tickerController:
        for tf, tfController in __tickerController.getTimeframes().items():
            for divergence in tfController.getDivergenceController().getActuals():
                power += abs(divergence.power)
                tfDivers = divers.setdefault(tf.name, [])
                tfDivers.append(divergence.toDict())
    data.setdefault('power', round(power))
    pyperclip.copy(str(json.dumps(data, indent = 4)))

def __openLink(link:str):
    webbrowser.register('chrome', None,
        webbrowser.BackgroundBrowser("C://Program Files//Google//Chrome//Application//chrome.exe"))
    webbrowser.get('chrome').open(link)

def __onOpenSpotLinkClicked():
    if not __tickerController:
        return
    __openLink(__url + __tickerController.getTicker())

def __onOpenFutureLinkClicked():
    if not __tickerController:
        return
    __openLink(__url + __tickerController.getFutureTicker() + '.P')

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
        __divergenceRatio.setStyleSheet(guiDefines.getEmptyProgressBarSheet())
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

def __updateDivergenceTable():
    global __table,__tickerController
    divergences = []
    for tf, tfController in __tickerController.getTimeframes().items():
        actuals = tfController.getDivergenceController().getActuals()
        actuals.sort(key = lambda info:info.power, reverse = True)
        for divergence in actuals:
            divergences.append((tf, divergence))

    if len(divergences) != __table.rowCount():
        __table.clearContents()
        __table.setRowCount(len(divergences))
        for row in range(len(divergences)):
            for column in range(__table.horizontalHeader().count()):
                item = QTableWidgetItem()
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                __table.setItem(row, column, item)

    row = 0
    headers = []
    for tf, divergence in divergences:
        color = guiDefines.bearColor if divergence.signal.name == 'BEAR' else guiDefines.bullColor
        trickedColor = guiDefines.trickedColor if divergence.tricked else guiDefines.defaultBgColor
        __table.item(row, 0).setText(divergence.type.name)
        __table.item(row, 0).setForeground(color)
        __table.item(row, 0).setBackground(trickedColor)
        __table.item(row, 1).setText(str(divergence.power))
        __table.item(row, 2).setText(str(round(divergence.breakPercents, 2)))
        __table.item(row, 3).setText(str(divergence.secondIndex - divergence.firstIndex))
        __table.item(row, 4).setText(divergence.firstCandle.time[:-5])
        headers.append(timeframe.timeframeToPrettyStr[tf])
        row += 1

    __table.setVerticalHeaderLabels(headers)


def update(ticker:str):
    global __tickerController
    __tickerController = watcherController.getTicker(ticker)

    __updateProgressBar()
    __updatePrice()
    for tabIndex in range(__tabs.count()):
        tabWidget = __tabs.widget(tabIndex)
        tf = timeframe.Timeframe[tabWidget.objectName()]
        tfController = __tickerController.getTimeframe(tf)

        __updateTabValues(tabWidget, tfController.getCandlesController())
    __updateDivergenceTable()
