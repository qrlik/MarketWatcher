
from PySide6.QtWidgets import QListWidgetItem

class ListTicketItem(QListWidgetItem):
    def __init__(self, ticker:str):
        self.__ticker = ticker
        super().__init__(ticker)

    def __lt__(self, other):
        return super().text() < other.text()
    
    __ticker:str = ''
