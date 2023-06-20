from PySide6.QtWidgets import QFrame,QPushButton

from models import timeframe
from systems import configController
from utilities import guiDefines
from widgets import watcherTable

__tfFilter:QFrame = None
__states:dict = {}
__generalButton:QPushButton = None
__buttons:dict = {}
__maxColumns = 3

def init(parent):
    global __tfFilter
    __tfFilter = parent.findChild(QFrame, 'timeframesFilter')
    __initGrid()

def isEnabled(tf:timeframe.Timeframe):
    return __states.get(tf, True)

def __checkAll(state):
    global __states
    for tf, button in __buttons.items():
        button.setChecked(state)
        __states[tf] = state
    watcherTable.update()

def __updateChecks(_):
    global __states,__generalButton
    allChecked = True
    for tf, button in __buttons.items():
        state = button.isChecked()
        __states[tf] = state
        allChecked &= state
    __generalButton.setChecked(allChecked)
    watcherTable.update()

def __createButton(name:str, callback):
    button = QPushButton(name)
    button.setCheckable(True)
    button.setChecked(True)
    button.setStyleSheet(guiDefines.getCheckedButtonSheet())
    button.clicked.connect(callback)
    return button

def __initGrid():
    global __generalButton,__buttons,__states

    layout = __tfFilter.layout()
    row = 0
    column = 0

    __generalButton = __createButton('All', __checkAll)
    layout.addWidget(__generalButton, row, column)
    row += 1

    for tf in configController.getTimeframes():
        button = __createButton(timeframe.getPrettyFormat(tf), __updateChecks)
        layout.addWidget(button, row, column)
        __buttons.setdefault(tf, button)
        __states.setdefault(tf, True)

        column += 1
        if column >= __maxColumns:
            row += 1
            column = 0
