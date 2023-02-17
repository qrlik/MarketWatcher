from PySide6.QtWidgets import QWidget,QComboBox,QPushButton,QListWidget,QListWidgetItem,QAbstractItemView,QFileDialog
import PySide6.QtCore

from models import timeframe
from widgets import configEditor
from systems import configController

__configWidget:QWidget = None
__configsList:QListWidget = None
__timeframeBox:QComboBox = None
__addButton:QPushButton = None
__loadButton:QPushButton = None
__saveButton:QPushButton = None
startButton:QPushButton = None

def init(widget:QWidget):
    __initVariables(widget)
    __initCombobox()
    __initAddButton()
    __initConfigList()
    __initLoadButton()
    __initSaveButton()

def getConfigsList():
    return __configsList

def update():
    __updateAddButtonState()
    __updateSaveButtonState()
    __updateStartButton()

def __updateAddButtonState():
    timeframeStr = __timeframeBox.currentText()
    configs = __configsList.findItems(timeframeStr, PySide6.QtCore.Qt.MatchFlag.MatchExactly)
    __addButton.setEnabled(len(configs) == 0)

def __updateSaveButtonState():
    __saveButton.setEnabled(__configsList.count() > 0)

def __updateStartButton():
    startButton.setEnabled(not configController.isEmpty())

def __initVariables(widget:QWidget):
    global __configWidget, __configsList, __timeframeBox, __addButton,__loadButton,__saveButton,startButton
    __configWidget = widget
    __configsList = widget.findChild(QListWidget, 'configsList')
    __timeframeBox = widget.findChild(QComboBox, 'timeframeBox')
    __addButton = widget.findChild(QPushButton, 'addButton')
    __loadButton = widget.findChild(QPushButton, 'loadButton')
    __saveButton = widget.findChild(QPushButton, 'saveButton')
    startButton = widget.findChild(QPushButton, 'startButton')

def __initCombobox():
    for tf in timeframe.Timeframe:
        if tf >= timeframe.Timeframe.ONE_HOUR:
            __timeframeBox.addItem(tf.name)

def __addConfigToList(text:str = ''):
    index = 0
    text = __timeframeBox.currentText() if len(text) == 0 else text
    value = timeframe.Timeframe[text]

    for i in range(__configsList.count()):
        if timeframe.Timeframe[__configsList.item(i).text()] < value:
            index += 1

    __configsList.insertItem(index, QListWidgetItem(text))
    configController.addConfig(text)
    update()

def __onAddButtonClick():
    __addConfigToList()

def __initAddButton():
    __timeframeBox.activated.connect(__updateAddButtonState)
    __addButton.clicked.connect(__onAddButtonClick)

def __initConfigList():
    __configsList.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
    __configsList.itemSelectionChanged.connect(configEditor.update)

def __getFilenameFromPath(path:str):
    splitedName = path[0].split('/')
    filename = splitedName.pop()
    return filename[:len(filename) - 5]

def __onLoadClick():
    path = QFileDialog.getOpenFileName(__configWidget, "Save Config Settings", "", "Bson Files (*.bson)")
    configController.load(__getFilenameFromPath(path))
    __configsList.clear()
    configEditor.update()
    for config in configController.getConfigs():
        __addConfigToList(config)

def __initLoadButton():
    __loadButton.clicked.connect(__onLoadClick)

def __onSaveClick():
    path = QFileDialog.getSaveFileName(__configWidget, "Save Config Settings", "", "Bson Files (*.bson)")
    configController.save(__getFilenameFromPath(path))

def __initSaveButton():
    __saveButton.clicked.connect(__onSaveClick)
