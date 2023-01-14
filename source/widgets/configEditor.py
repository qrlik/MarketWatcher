from PySide6.QtWidgets import QWidget,QPushButton,QListWidget

from systems import configController

__editor:QWidget = None
__editorList:QListWidget = None
__button:QPushButton = None

def init(editor:QWidget, editorList:QListWidget):
    __initVariables(editor, editorList)
    #initGrid
    __initDeleteButton()

def __initVariables(editor:QWidget, editorList:QListWidget):
    global __editor,__button, __editorList
    __editor = editor
    __editorList = editorList
    __button = __editor.findChild(QPushButton, 'deleteButton')

def __onDelete():
    items = __editorList.selectedItems()
    configController.deleteConfig(items[0].text())
    __editorList.takeItem(__editorList.row(items[0]))
    updateConfigEditor()
    #__updateAddButtonState

def __initDeleteButton():
    __button.clicked.connect(__onDelete)

def updateConfigEditor():
    items = __editorList.selectedItems()
    __button.setEnabled(len(items) > 0)
