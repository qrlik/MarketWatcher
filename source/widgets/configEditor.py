from PySide6.QtWidgets import QWidget,QPushButton,QListWidget,QCheckBox
import PySide6.QtCore

from systems import configController
from widgets import configsWidget

__editor:QWidget = None
__editorList:QListWidget = None
__configGrid:QWidget = None
__button:QPushButton = None

def init(editor:QWidget, editorList:QListWidget):
    __initVariables(editor, editorList)
    __initGrid()
    __initDeleteButton()

def update():
    __updateGrid()
    __updateDeleteButton()

def __updateGrid():
    items = __editorList.selectedItems()
    itemText = items[0].text() if len(items) > 0 else ''
    for box in __configGrid.findChildren(QCheckBox):
        state = configController.getState(itemText, box.text())
        box.setCheckState(PySide6.QtCore.Qt.CheckState.Checked if state else PySide6.QtCore.Qt.CheckState.Unchecked)
        box.setEnabled(len(items) > 0)

def __updateDeleteButton():
    __button.setEnabled(len(__editorList.selectedItems()) > 0)

def __initVariables(editor:QWidget, editorList:QListWidget):
    global __editor,__button, __editorList,__configGrid
    __editor = editor
    __editorList = editorList
    __configGrid = __editor.findChild(QWidget, 'configGrid')
    __button = __editor.findChild(QPushButton, 'deleteButton')

def __initGrid():
    pass # to do

def __onDelete():
    items = __editorList.selectedItems()
    configController.deleteConfig(items[0].text())
    __editorList.takeItem(__editorList.row(items[0]))
    configsWidget.update()
    update()

def __initDeleteButton():
    __button.clicked.connect(__onDelete)
