from PySide6.QtWidgets import QFrame,QPushButton,QHBoxLayout

from models import timeframe
from systems import configController
from utilities import guiDefines
from widgets import watcherTable

__tfFilter:QFrame = None
__tfStates:dict = {}
__trickState:dict = {}

__generalButton:QPushButton = None
__buttons:dict = {}
__trickButtons:dict = {}

__maxColumns = 2

def init(parent):
    global __tfFilter
    __tfFilter = parent.findChild(QFrame, 'timeframesFilter')
    __initGrid()

def isTfEnabled(tf:timeframe.Timeframe):
    return __tfStates.get(tf, False)

def isDivergenceTricked(tf:timeframe.Timeframe):
    return __trickState.get(tf, False)

def __checkAll(state):
    global __tfStates
    for tf, button in __buttons.items():
        button.setChecked(state)
        __tfStates[tf] = state
    watcherTable.update()

def __updateChecks():
    global __tfStates,__generalButton
    allChecked = True
    for tf, button in __buttons.items():
        state = button.isChecked()
        __tfStates[tf] = state
        allChecked &= state
    __generalButton.setChecked(allChecked)
    watcherTable.update()

def __updateTricked():
    global __trickState
    for tf, button in __trickButtons.items():
        state = button.isChecked()
        __trickState[tf] = state
    watcherTable.update()

def __createButtons(name:str, tfCallback, trickCallback):
    layout = QHBoxLayout()

    tfButton = QPushButton(name)
    tfButton.setCheckable(True)
    tfButton.setChecked(False)
    tfButton.setStyleSheet(guiDefines.getCheckedButtonSheet())
    tfButton.clicked.connect(tfCallback)
    layout.addWidget(tfButton)

    if trickCallback is not None:
        trickButton = QPushButton('T')
        trickButton.setCheckable(True)
        trickButton.setChecked(False)
        trickButton.setStyleSheet(guiDefines.getCheckedButtonSheet())
        trickButton.clicked.connect(trickCallback)
        trickButton.setFixedWidth(40)
        layout.addWidget(trickButton)
        return (layout, tfButton, trickButton)

    return (layout, tfButton)

def __initGrid():
    global __generalButton,__buttons,__tfStates

    layout = __tfFilter.layout()
    row = 0
    column = 0

    genLayout, __generalButton = __createButtons('All', __checkAll, None)
    layout.addLayout(genLayout, row, column)
    row += 1

    for tf in configController.getTimeframes():
        tfLayout, tfButton, trickButton = __createButtons(timeframe.getPrettyFormat(tf), __updateChecks, __updateTricked)
        layout.addLayout(tfLayout, row, column)

        __buttons.setdefault(tf, tfButton)
        __trickButtons.setdefault(tf, trickButton)

        __tfStates.setdefault(tf, False)
        __trickState.setdefault(tf, False)

        column += 1
        if column >= __maxColumns:
            row += 1
            column = 0
