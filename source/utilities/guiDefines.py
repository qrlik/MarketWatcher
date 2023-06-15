from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

bullColor:QColor = Qt.GlobalColor.darkGreen
bearColor:QColor = Qt.GlobalColor.darkRed
defaultColor:QColor = Qt.GlobalColor.white

def getDefaultProgressBarSheet():
    return 'QProgressBar { background: darkRed } QProgressBar::chunk { background: darkGreen }'

def getEmptyProgressBarSheed():
    return 'QProgressBar { background: darkGray } QProgressBar::chunk { background: darkGray }'