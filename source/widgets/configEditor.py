from PySide6.QtWidgets import QWidget,QPushButton,QListWidget,QCheckBox,QComboBox
import PySide6.QtCore

from systems import configController
from systems import settingsController
from widgets import configsWidget

__editor:QWidget = None
__editorList:QListWidget = None
__configGrid:QWidget = None
__nameBox:QComboBox = None
__valueBox:QComboBox = None
__button:QPushButton = None
__checkedByUser = True

def init(editor:QWidget, editorList:QListWidget):
    __initVariables(editor, editorList)
    __initGrid()
    __initDeleteButton()
    update()

def update():
    __updateGrid()
    __updateDeleteButton()

def __updateGrid():
    global __checkedByUser
    items = __editorList.selectedItems()
    itemText = items[0].text() if len(items) > 0 else ''
    for box in __configGrid.findChildren(QCheckBox):
        state = configController.getState(itemText, box.text())
        __checkedByUser = False
        box.setCheckState(PySide6.QtCore.Qt.CheckState.Checked if state else PySide6.QtCore.Qt.CheckState.Unchecked)
        __checkedByUser = True
        box.setEnabled(len(items) > 0)

def __updateDeleteButton():
    __button.setEnabled(len(__editorList.selectedItems()) > 0)

def __initVariables(editor:QWidget, editorList:QListWidget):
    global __editor,__button, __editorList,__configGrid,__nameBox,__valueBox
    __editor = editor
    __editorList = editorList
    __configGrid = __editor.findChild(QWidget, 'configGrid')
    __nameBox = __configGrid.findChild(QComboBox, 'nameBox')
    __valueBox = __configGrid.findChild(QComboBox, 'valueBox')
    __button = __editor.findChild(QPushButton, 'deleteButton')

def __onCheckStateChanged():
    items = __editorList.selectedItems()
    if not __checkedByUser or len(items) == 0:
        return
    timeframe = items[0].text()
    for box in __configGrid.findChildren(QCheckBox):
        value = box.checkState() == PySide6.QtCore.Qt.CheckState.Checked
        configController.updateConfig(timeframe, box.text(), value)
    configsWidget.update()

def __initGrid():
    __nameBox.currentIndexChanged.connect(updateValueBox)
    for name, _ in settingsController.getConfig('globalConfigs').items():
        __nameBox.addItem(name)
    for box in __configGrid.findChildren(QCheckBox):
        box.stateChanged.connect(__onCheckStateChanged)

def updateValueBox():
    if __nameBox is None:
        return
    
    if __nameBox.currentText() == 'maDeltaTimeframe':
        __valueBox.clear()
        for i in range(__editorList.count()):
            __valueBox.addItem(__editorList.item(i).text())

def __onDelete():
    items = __editorList.selectedItems()
    if len(items) == 0:
        return
    configController.deleteConfig(items[0].text())
    __editorList.takeItem(__editorList.row(items[0]))
    configsWidget.update()
    update()

def __initDeleteButton():
    __button.clicked.connect(__onDelete)
