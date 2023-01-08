# This Python file uses the following encoding: utf-8
import os
from pathlib import Path

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import QFile
from PySide6.QtUiTools import QUiLoader


class MarketWatcher(QWidget):
    def __init__(self):
        super(MarketWatcher, self).__init__()
        self.loadUi()

    def loadUi(self):
        loader = QUiLoader()
        path = os.fspath(Path(__file__).resolve().parent / "form.ui")
        uiFile = QFile(path)
        uiFile.open(QFile.ReadOnly)
        loader.load(uiFile, self)
        uiFile.close()
