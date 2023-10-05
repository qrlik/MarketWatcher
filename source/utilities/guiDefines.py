from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

bullColor:QColor = Qt.GlobalColor.darkGreen
bearColor:QColor = Qt.GlobalColor.darkRed
trickedColor:QColor = Qt.GlobalColor.gray
notViewedColor:QColor = QColor(255,127,80)
zeroColor:QColor = Qt.GlobalColor.darkGray
invalidColor:QColor = Qt.GlobalColor.blue
defaultBgColor:QColor = QColor(45, 45, 45)
defaultFontColor:QColor = Qt.GlobalColor.white

def getDefaultProgressBarSheet():
    return 'QProgressBar { background: darkRed } QProgressBar::chunk { background: darkGreen }'

def getEmptyProgressBarSheet():
    return 'QProgressBar { background: darkGray } QProgressBar::chunk { background: darkGray }'

def getCheckedButtonSheet():
    return 'QPushButton::checked { background: lightGray; color: black }'