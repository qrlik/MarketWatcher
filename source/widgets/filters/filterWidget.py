from PySide6.QtWidgets import QFrame

from widgets.filters import timeframesFilter

__widget:QFrame = None

def init(parent):
    global __widget
    __widget = parent.findChild(QFrame, 'filterWidget')
    __widget.setFixedWidth(550)
    timeframesFilter.init(__widget)
