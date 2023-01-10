from PySide6.QtWidgets import QWidget,QComboBox,QPushButton,QListWidget,QListWidgetItem
import PySide6.QtCore

from models import enums
from utilities import utils

__configWidget = None
__configList = None
__timeframeBox = None
__addButton = None

def init(widget:QWidget):
    initVariables(widget)
    #initList + load last settings
    initCombobox()
    initAddButton()

def initVariables(widget:QWidget):
    global __configWidget, __configList, __timeframeBox, __addButton
    __configWidget = widget
    __configList = widget.findChild(QListWidget, 'configList')
    __timeframeBox = widget.findChild(QComboBox, 'timeframeBox')
    __addButton = widget.findChild(QPushButton, 'addButton')

def initCombobox():
    for timeframe in enums.Timeframe:
        __timeframeBox.addItem(timeframe.name)

def initAddButton():
    __timeframeBox.activated.connect(updateAddButtonState)
    __addButton.clicked.connect(onAddButtonClick)
    updateAddButtonState()

def updateAddButtonState():
    timeframeStr = __timeframeBox.currentText()
    configs = __configList.findItems(timeframeStr, PySide6.QtCore.Qt.MatchFlag.MatchExactly)
    __addButton.setEnabled(len(configs) == 0)

def addConfigToList():
    index = 0
    text = __timeframeBox.currentText()
    value = enums.Timeframe[text]

    for i in range(__configList.count()):
        if enums.Timeframe[__configList.item(i).text()] < value:
            index += 1

    __configList.insertItem(index, QListWidgetItem(text))

def onAddButtonClick():
    addConfigToList()
    updateAddButtonState()

