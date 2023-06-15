
from PySide6.QtWidgets import QTableWidget,QAbstractItemView
from PySide6.QtCore import Qt

from systems import watcherController

from widgets import infoWidget
from widgets.watcherTableItems import tickerNameItem
from widgets.watcherTableItems import divergenceAccumulatePowerItem
from widgets.watcherTableItems import divergenceBearPowerItem
from widgets.watcherTableItems import divergenceBullPowerItem

__watcherTable:QTableWidget = None
__sortColumn = 1

def setTable(table):
    global __watcherTable
    __watcherTable = table
    
def initList():
    global __watcherTable
    __watcherTable.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
    __watcherTable.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
    __watcherTable.itemSelectionChanged.connect(__updateInfoWidget)
    tickers = watcherController.getTickers().keys()
    __watcherTable.setRowCount(len(tickers))
    __watcherTable.setColumnCount(4)
    __watcherTable.setHorizontalHeaderLabels(['Ticker', 'Power', 'Bull Power,%', 'Bear Power,%'])
    __watcherTable.horizontalHeader().sectionClicked.connect(__updateSortOrder)

    row = 0
    for ticker in tickers:
        __watcherTable.setItem(row, 0, tickerNameItem.TickerNameItem(ticker))
        __watcherTable.setItem(row, 1, divergenceAccumulatePowerItem.DivergenceAccumulatePowerItem(ticker))
        __watcherTable.setItem(row, 2, divergenceBullPowerItem.DivergenceBullPowerItem(ticker))
        __watcherTable.setItem(row, 3, divergenceBearPowerItem.DivergenceBearPowerItem(ticker))
        row += 1

def updateViewedDivergence():
    global __watcherTable
    selectedItems = __watcherTable.selectedItems()
    if len(selectedItems) == 0:
        return
    selectedItems[1].update()

def __sortList():
    global __watcherTable,__sortColumn
    if __sortColumn == 0:
        __watcherTable.sortItems(__sortColumn, order = Qt.SortOrder.AscendingOrder)
    elif __sortColumn == 1:
        __watcherTable.sortItems(__sortColumn, order = Qt.SortOrder.DescendingOrder)

def update():
    __updateList()
    __updateInfoWidget(False)

def __updateList():
    global __watcherTable,__sortColumn
    for r in range(__watcherTable.rowCount()):
        for c in range(0, __watcherTable.columnCount()):
            __watcherTable.item(r, c).update()
    __sortList()

def __updateSortOrder(index):
    global __sortColumn
    if index != __sortColumn and (index == 0 or index == 1):
        __sortColumn = index
        __sortList()

def __updateInfoWidget(byClick=True):
    global __watcherTable
    selectedItems = __watcherTable.selectedItems()
    if len(selectedItems) == 0:
        return
    infoWidget.update(selectedItems[0].getTicker(), byClick)
    