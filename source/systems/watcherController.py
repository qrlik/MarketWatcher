from api import api
from models import enums

def getTickersList():
    info = api.getExchangeInfo()
    
    x = 5
    