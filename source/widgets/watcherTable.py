from PySide6.QtWidgets import QTableWidget,QAbstractItemView,QProgressBar,QHeaderView
from PySide6.QtCore import Qt

from systems import watcherController

from widgets import infoWidget
from widgets.watcherTableItems import tickerNameItem
from widgets.watcherTableItems import channelPowerItem
from utilities import workMode

__watcherTable:QTableWidget = None
__bullBar:QProgressBar = None
__bearBar:QProgressBar = None
__emptyBar:QProgressBar = None
__headers:list = ['Ticker', 'Power' ]
__sortColumn = 1

def init(parent):
    global __watcherTable,__bullBar,__bearBar,__emptyBar
    __watcherTable = parent.findChild(QTableWidget, 'watcherTable')
    __bullBar = parent.findChild(QProgressBar, 'bullBar')
    __bearBar = parent.findChild(QProgressBar, 'bearBar')
    __emptyBar = parent.findChild(QProgressBar, 'emptyBar')
    __initTable()
    __initRatio()

def __initTable():
    global __watcherTable,__headers
    __watcherTable.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
    __watcherTable.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
    __watcherTable.itemSelectionChanged.connect(__onItemClicked)
    __watcherTable.setColumnCount(len(__headers))
    __watcherTable.setHorizontalHeaderLabels(__headers)
    __watcherTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    __watcherTable.horizontalHeader().sectionClicked.connect(__updateSortOrder)

def __initRatio():
    global __bullBar,__bearBar,__emptyBar
    if workMode.isStock():
        __bullBar.deleteLater()
        __bearBar.deleteLater()
        __emptyBar.deleteLater()
    else:
        __bullBar.setStyleSheet('QProgressBar::chunk { background: darkGreen }')
        __bearBar.setStyleSheet('QProgressBar::chunk { background: darkRed }')
        __emptyBar.setStyleSheet('QProgressBar::chunk { background: darkGray }')

def initList():
    global __watcherTable
    tickers = watcherController.getTickers().keys()
    __watcherTable.setRowCount(len(tickers))
    row = 0
    for ticker in tickers:
        __watcherTable.setItem(row, 0, tickerNameItem.TickerNameItem(ticker))
        __watcherTable.setItem(row, 1, channelPowerItem.ChannelPowerItem(ticker))
        row += 1

def sortList():
    global __watcherTable,__sortColumn
    if __sortColumn == 0:
        __watcherTable.sortItems(__sortColumn, order = Qt.SortOrder.AscendingOrder)
    elif __sortColumn == 1:
        __watcherTable.sortItems(__sortColumn, order = Qt.SortOrder.DescendingOrder)

def update():
    __updateRatio()
    __updateList()
    if workMode.isCrypto():
        __updateInfoWidget(False)

def __updateRatio():
    if workMode.isStock():
        return
    global __bullBar,__bearBar,__emptyBar,__watcherTable
    bullTickers = 0
    bearTickers = 0
    summary = len(watcherController.getTickers())
    if summary == 0:
        return
    for _, tickerController in watcherController.getTickers().items():
        bullPower = 0.0
        bearPower = 0.0
        for _, timeframeController in tickerController.getFilteredTimeframes().items():
            powers = timeframeController.getDivergenceController().getRegularPowers()
            bullPower += powers.bullPower
            bearPower += powers.bearPower
        isBullPower = bullPower > 0.0
        isBearPower = bearPower > 0.0
        if isBullPower and bullPower >= bearPower:
            bullTickers += 1
        if isBearPower and bearPower >= bullPower:
            bearTickers += 1
    bullFactor = bullTickers / summary
    bearFactor = bearTickers / summary
    emptyFactor = (summary - bullTickers - bearTickers) / summary
    __bullBar.setFixedWidth(bullFactor * __watcherTable.width())
    __bearBar.setFixedWidth(bearFactor * __watcherTable.width())
    __emptyBar.setFixedWidth(emptyFactor * __watcherTable.width())


def __updateList():
    global __watcherTable
    for r in range(__watcherTable.rowCount()):
        for c in range(0, __watcherTable.columnCount()):
            __watcherTable.item(r, c).update()
    sortList()

def __updateSortOrder(index):
    global __sortColumn
    if index != __sortColumn and (index == 0 or index == 1):
        __sortColumn = index
        sortList()

def __onItemClicked():
    global __watcherTable
    selectedItems = __watcherTable.selectedItems()
    if len(selectedItems) == 0:
        return
    __updateInfoWidget(True)
    selectedItems[1].update()


def __updateInfoWidget(byClick):
    global __watcherTable
    selectedItems = __watcherTable.selectedItems()
    if len(selectedItems) == 0:
        return
    infoWidget.update(selectedItems[0].getTicker(), byClick)
    