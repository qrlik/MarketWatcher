from PySide6.QtWidgets import QWidget,QComboBox,QPushButton,QListWidget,QListWidgetItem,QAbstractItemView
import PySide6.QtCore

from models import enums
from widgets import configEditor
from systems import configController

__configWidget:QWidget = None
__configsList:QListWidget = None
__timeframeBox:QComboBox = None
__addButton:QPushButton = None

def getConfigsList():
    return __configsList

def init(widget:QWidget):
    __initVariables(widget)
    #initList + load last settings
    __initCombobox()
    __initAddButton()
    __initConfigList()

def __initVariables(widget:QWidget):
    global __configWidget, __configsList, __timeframeBox, __addButton
    __configWidget = widget
    __configsList = widget.findChild(QListWidget, 'configsList')
    __timeframeBox = widget.findChild(QComboBox, 'timeframeBox')
    __addButton = widget.findChild(QPushButton, 'addButton')

def __initCombobox():
    for timeframe in enums.Timeframe:
        __timeframeBox.addItem(timeframe.name)

def __addConfigToList():
    index = 0
    text = __timeframeBox.currentText()
    value = enums.Timeframe[text]

    for i in range(__configsList.count()):
        if enums.Timeframe[__configsList.item(i).text()] < value:
            index += 1

    __configsList.insertItem(index, QListWidgetItem(text))
    configController.addConfig(text)

def __onAddButtonClick():
    __addConfigToList()
    __updateAddButtonState()

def __updateAddButtonState():
    timeframeStr = __timeframeBox.currentText()
    configs = __configsList.findItems(timeframeStr, PySide6.QtCore.Qt.MatchFlag.MatchExactly)
    __addButton.setEnabled(len(configs) == 0)

def __initAddButton():
    __timeframeBox.activated.connect(__updateAddButtonState)
    __addButton.clicked.connect(__onAddButtonClick)
    __updateAddButtonState()

def __initConfigList():
    __configsList.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
    __configsList.itemSelectionChanged.connect(configEditor.updateConfigEditor)


