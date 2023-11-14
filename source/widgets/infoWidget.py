from PySide6.QtWidgets import QFrame,QSlider,QCheckBox,QLabel,QVBoxLayout,QHBoxLayout,QTabWidget,QWidget,QAbstractItemView,QTableWidget,QTableWidgetItem,QHeaderView,QPushButton,QProgressBar
from PySide6.QtCore import Qt

from models import candle
from models import timeframe
from systems import cacheController
from systems import configController
from systems import userDataController
from systems import watcherController
from utilities import guiDefines
from utilities import workMode
from utilities import utils

from datetime import date
import pyperclip
import json
import webbrowser

__widget:QFrame = None
__nameValue:QLabel = None
__categoryValue:QLabel = None
__priceValue:QLabel = None
__viewedAgo:QLabel = None
__viewedDate:QLabel = None
__boredBox:QCheckBox = None
__boredAgo:QLabel = None
__boredDate:QLabel = None
__boredCounter:QLabel = None
__boredSlider:QSlider = None
__tabs:QTabWidget = None
__table:QTableWidget = None
__dataButton:QPushButton = None
__linkButton:QPushButton = None
__divergenceRatio:QProgressBar = None
__tickerController = None
__url = 'https://www.tradingview.com/chart/?symbol='

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
    __initBored()

def __initValues():
    global __widget, __nameValue, __categoryValue, __priceValue, __tabs, __dataButton,__divergenceRatio,__linkButton,__table, \
    __viewedAgo, __viewedDate, __boredBox, __boredAgo, __boredDate, __boredCounter, __boredSlider

    __nameValue = __widget.findChild(QLabel, 'nameValue')
    __categoryValue = __widget.findChild(QLabel, 'categoryValue')
    __priceValue = __widget.findChild(QLabel, 'priceValue')
    __viewedAgo = __widget.findChild(QLabel, 'viewedAgoLabel')
    __viewedDate = __widget.findChild(QLabel, 'viewedDateLabel')
    __boredBox = __widget.findChild(QCheckBox, 'boredBox')
    __boredAgo = __widget.findChild(QLabel, 'boredAgoLabel')
    __boredDate = __widget.findChild(QLabel, 'boredDateLabel')
    __boredCounter = __widget.findChild(QLabel, 'boredCountLabel')
    __boredSlider = __widget.findChild(QSlider, 'boredSlider')
    __tabs = __widget.findChild(QTabWidget, 'tabWidget')
    __table = __widget.findChild(QTableWidget, 'tableWidget')
    __divergenceRatio = __widget.findChild(QProgressBar, 'divergenceRatio')
    __dataButton = __widget.findChild(QPushButton, 'copyDataButton')
    __linkButton = __widget.findChild(QPushButton, 'openLinkButton')

def __initButtons():
    __dataButton.clicked.connect(__onDataCopyClicked)

    __linkButton.setText('Spot')
    __linkButton.clicked.connect(__onOpenSpotLinkClicked)

    if workMode.isCrypto():
        layout = __widget.findChild(QHBoxLayout, 'positionLayout')
        futureButton = QPushButton('Future')
        layout.addWidget(futureButton)
        futureButton.clicked.connect(__onOpenFutureLinkClicked)

def __initTabs():
    __tabs.tabBar().setDocumentMode(True)
    __tabs.tabBar().setExpanding(True)
    __tabs.setFixedHeight(105)
    __tabs.tabBarClicked.connect(__onTabClicked)

    for tf in configController.getTimeframes():
        tabWidget = QWidget()
        tabWidget.setObjectName(tf.name)
        __tabs.addTab(tabWidget, timeframe.getPrettyFormat(tf))
        tabWidget.setLayout(QVBoxLayout())
        __initCandleTime(tabWidget)
        __initRsi(tabWidget)
        __initAtr(tabWidget)
        tabWidget.layout().addStretch()

def __initProgressBar():
    global __divergenceRatio
    __divergenceRatio.setStyleSheet(guiDefines.getEmptyProgressBarSheet())

def __initCandleTime(tab:QWidget):
    layout = QHBoxLayout()
    layout.setObjectName('timeLayout')
    tab.layout().addLayout(layout)

    rsiLabel = QLabel('Date')
    rsiLabel.setObjectName('dateLabel')
    layout.addWidget(rsiLabel)
    layout.addStretch()

    rsiValue = QLabel('-')
    rsiValue.setObjectName('dateValue')
    layout.addWidget(rsiValue)

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

def __initBored():
    global __boredBox,__boredSlider,__boredCounter
    __boredBox.clicked.connect(__onBoredClicked)
    __boredBox.setStyleSheet(guiDefines.getCheckBoxSheet())
    __boredSlider.valueChanged.connect(__updateBoredCount)

def __updateBoredCount(count):
    global __boredCounter,__boredSlider
    if __tickerController is None:
        return
    if count is None:
        __boredSlider.setValue(cacheController.getBoredCount(__tickerController.getTicker()))
    else:
        __boredCounter.setText(str(count) + ' ')
        cacheController.setBoredCount(__tickerController.getTicker(), count)

def __onTabClicked():
    if __tickerController is None:
        return
    
    for _, tfController in __tickerController.getTimeframes().items():
        for divergence in tfController.getDivergenceController().getActuals():
            time1 = divergence.firstCandle.time
            time2 = divergence.secondCandle.time
            cacheController.setDivergenceViewed(__tickerController.getTicker(), tfController.getTimeframe().name, time1, time2, True)
            divergence.viewed = True

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
    data.setdefault('power', power)
    pyperclip.copy(str(json.dumps(data, indent = 4)))

def __openLink(link:str):
    webbrowser.register('chrome', None,
        webbrowser.BackgroundBrowser("C://Program Files//Google//Chrome//Application//chrome.exe"))
    webbrowser.get('chrome').open(link)

def __onOpenSpotLinkClicked():
    if not __tickerController:
        return
    url = __url if workMode.isStock() else __url + 'BINANCE:'
    ticker = __tickerController.getTicker()
    cacheController.setDatestamp(ticker, cacheController.DateStamp.VIEWED, utils.getCurrentTimeSeconds())
    __openLink(url + ticker)

def __onOpenFutureLinkClicked():
    if not __tickerController:
        return
    url = __url if workMode.isStock() else __url + 'BINANCE:'
    ticker = __tickerController.getTicker()
    cacheController.setDatestamp(ticker, cacheController.DateStamp.VIEWED, utils.getCurrentTimeSeconds())
    __openLink(url + ticker + '.P')

def __onBoredClicked(state):
    if __tickerController is None:
        return
    time = utils.getCurrentTimeSeconds() if state else None
    cacheController.setDatestamp(__tickerController.getTicker(), cacheController.DateStamp.BORED, time)
    __updateBored(__tickerController.getTicker())

def __updateName():
    if __tickerController:
        __nameValue.setText(__tickerController.getName())

def __updateCategory():
    if __tickerController:
        __categoryValue.setText(__tickerController.getIndustry() + '-' + __tickerController.getCategory())

def __updatePrice():
    price = None
    if __tickerController:
        for _, controller in __tickerController.getTimeframes().items():
            lastCandle = controller.getCandlesController().getLastCandle()
            price = lastCandle.close if lastCandle else None
            break
    __priceValue.setText(str(price))

def __updateInfo():
    __updatePrice()
    __updateName()
    __updateCategory()

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

def __updateTabValues(tabWidget:QWidget, candlesController):
    candle = None
    candles = candlesController.getFinishedCandles()
    if len(candles) > 0:
        candle = candles[-1]

    dateValue = tabWidget.findChild(QLabel, 'dateValue')
    dateValue.setText(str(candle.time if candle else candle))

    atrValue = tabWidget.findChild(QLabel, 'atrValue')
    atrValue.setText(str(candle.atr if candle else candle))

    rsiValue = tabWidget.findChild(QLabel, 'rsiValue')
    rsiValue.setText(str(candle.rsi if candle else candle))

def __updateViewed(ticker):
    global __viewedAgo, __viewedDate
    ago = '-'
    time = '-'
    timestamp = cacheController.getDatestamp(ticker, cacheController.DateStamp.VIEWED)
    if timestamp:
        now = date.fromtimestamp(utils.getCurrentTimeSeconds())
        stamp = date.fromtimestamp(timestamp)
        diff = now - stamp
        ago = str(diff.days) + 'd '
        time = candle.getPrettyTime(timestamp * 1000, timeframe.Timeframe.ONE_DAY)
    __viewedAgo.setText(ago)
    __viewedDate.setText(time)

def __updateBored(ticker):
    global __boredAgo, __boredDate
    ago = '-'
    time = '-'
    timestamp = cacheController.getDatestamp(ticker, cacheController.DateStamp.BORED)
    if timestamp:
        now = date.fromtimestamp(utils.getCurrentTimeSeconds())
        stamp = date.fromtimestamp(timestamp)
        diff = now - stamp
        ago = str(diff.days)
        time = candle.getPrettyTime(timestamp * 1000, timeframe.Timeframe.ONE_DAY)
    __boredAgo.setText(ago)
    __boredDate.setText(time)
    __boredBox.setChecked(bool(timestamp))

def __updateDatestamps(ticker):
    __updateViewed(ticker)
    __updateBored(ticker)
    __updateBoredCount(None)

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
        __table.item(row, 1).setForeground(guiDefines.defaultFontColor if divergence.viewed else guiDefines.notViewedColor)
        __table.item(row, 2).setText(str(round(divergence.breakPercents, 2)))
        __table.item(row, 3).setText(str(divergence.secondIndex - divergence.firstIndex))
        __table.item(row, 4).setText(divergence.firstCandle.time[:-5])
        headers.append(timeframe.timeframeToPrettyStr[tf])
        row += 1

    __table.setVerticalHeaderLabels(headers)


def update(ticker:str, byClick):
    global __tickerController
    __tickerController = watcherController.getTicker(ticker)

    __updateProgressBar()
    __updateInfo()
    for tabIndex in range(__tabs.count()):
        tabWidget = __tabs.widget(tabIndex)
        tf = timeframe.Timeframe[tabWidget.objectName()]
        tfController = __tickerController.getTimeframe(tf)

        __updateTabValues(tabWidget, tfController.getCandlesController())
        __updateDatestamps(ticker)

    __updateDivergenceTable()
    if byClick:
        __onTabClicked()
