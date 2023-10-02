import requests
import pandas as pd
import ftplib
import io
import time
from enum import IntEnum
from datetime import datetime

from models import candle
from models import timeframe
from utilities import utils

class Weekday(IntEnum):
    MONDAY = 1,
    TUESDAY = 2,
    WEDNESDAY = 3,
    THURSDAY = 4,
    FRIDAY = 5,
    SATURDAY = 6,
    SUNDAY = 7

def isWeekend(day:Weekday):
    return day == Weekday.SATURDAY or day == Weekday.SUNDAY

def getPricePrecision(price):
    if price >= 1.0:
        return 2
    return 4

try:
    from requests_html import HTMLSession
except Exception:
    print("""Warning - Certain functionality 
             requires requests_html, which is not installed.
             
             Install using: 
             pip install requests_html
             
             After installation, you may have to restart your Python session.""")

    
base_url = "https://query1.finance.yahoo.com/v8/finance/chart/"

__oneDay = 86400
__postSession = 19800 # 5,5 hours
__regularSession = 23400 # 6,5 hours
__postSession = 14400 # 4 hours
__tradeSession = __postSession + __regularSession + __postSession

def __getExpectedCloseTime(openTime, interval):
    dt = datetime.fromtimestamp(openTime)
    
    if interval == '1d':
        if isWeekend(dt.isoweekday()):
            return None
        return openTime + __regularSession + __postSession
    
    elif interval == '1wk':
        if isWeekend(dt.isoweekday()):
            return None
        return openTime + (5 - dt.isoweekday()) * __oneDay + __tradeSession
    
    elif interval == '1mo':
        lastWorkDay = openTime
        day = openTime + __oneDay
        while True:
            nextDt = datetime.fromtimestamp(day)
            if nextDt.month == dt.month:
                if not isWeekend(nextDt.isoweekday()):
                    lastWorkDay = day
                day += __oneDay
            else:
                if lastWorkDay == openTime:
                    return None
                return lastWorkDay + __tradeSession
    else:
        utils.logError('yahoo __getExpectedCloseTime invalid interval')

def isExpectNewCandles(openTime, interval):
    if interval not in ['1d', '1wk', '1mo']:
        utils.logError('yahoo isExpectNewCandles invalid interval')
        return
    
    openDt = datetime.fromtimestamp(openTime)
    lastTimestamp = openTime + __oneDay
    while True:
        dt = datetime.fromtimestamp(lastTimestamp)
        if interval == '1d' and not isWeekend(dt.isoweekday()) \
        or interval == '1wk' and dt.isoweekday() == Weekday.MONDAY \
        or interval == '1mo' and dt.month != openDt.month:
            closeTime = __getExpectedCloseTime(lastTimestamp, interval)
            return closeTime < time.time()
        lastTimestamp += __oneDay

def __isValidCandle(candle, regularMarketTime, sessionStartTime, sessionEndTime):
    curTime = int(time.time())
    if candle[0] == regularMarketTime:
        return False
    if candle[0] >= curTime:
        return False
    if candle[1] == None \
    or candle[2] == None \
    or candle[3] == None \
    or candle[4] == None:
        return False
    if curTime <= sessionEndTime:
        if not candle[5] or candle[5] >= sessionStartTime:
            return False
    if candle[0] % 10 > 0:
        utils.logError('yahoo isValidCandle not zero tail')
    return True
    
def __parseResponse(data, interval):
    c = candle.Candle()
    c.interval = timeframe.yahooApiStrToTf[interval]
    c.openTime = data[0] * 1000
    c.time = candle.getPrettyTime(c.openTime, c.interval)
    c.open = round(data[1], getPricePrecision(data[1]))
    c.high = round(data[2], getPricePrecision(data[2]))
    c.low = round(data[3], getPricePrecision(data[3]))
    c.close = round(data[4], getPricePrecision(data[4]))
    c.closeTime = data[5] * 1000
    return c

def build_url(ticker, start_date = None, end_date = None, interval = "1d"):
    if end_date is None:  
        end_seconds = int(int(time.time()))
    else:
        end_seconds = int(end_date)
        
    if start_date is None or int(start_date) < 7223400:
        start_seconds = 7223400  
    else:
        start_seconds = int(start_date)
    
    site = base_url + ticker
    
    params = {"period1": start_seconds, "period2": end_seconds, "interval": interval.lower()} #, "events": "div,splits"}
    return site, params

def is_valid_data(ticker, data):
    # to do add check for price prec
    # currency = data['meta']['currency']
    # precision = data['meta']['priceHint']
    # if isinstance(currency, str) and currency != 'USD':
    #     utils.logError('yahoo get_data ' + ticker + ' wrong currency')
    #     return False
    # if isinstance(precision, int) and precision != 2:
    #     utils.logError('yahoo get_data ' + ticker + ' wrong precision')
    #     return False
    return True

def get_data(ticker, intervalStr, start_date = None, end_date = None, ):
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

    '''Downloads historical stock price data into a pandas data frame.  Interval
       must be "1d", "1wk", "1mo", or "1m" for daily, weekly, monthly, or minute data.
       Intraday minute data is limited to 7 days.
       @param: ticker
       @param: start_date = None
       @param: end_date = None
       @param: index_as_date = True
       @param: interval = "1d"
    '''

    if intervalStr not in ("1d", "1wk", "1mo"):
        utils.logError('yahoo get_data invalid interval')
        return
    
    # build and connect to URL
    site, params = build_url(ticker, start_date, end_date, intervalStr)
    try:
        resp = requests.get(site, params = params, headers = headers)
    except requests.exceptions.ConnectTimeout:
        utils.logError('yahoo get_data ConnectTimeout')
        return []
    except requests.exceptions.RequestException as e:
        utils.logError('yahoo get_data RequestException ' + ticker + ' ' + e.strerror)
        return []

    if not resp.ok:
        code = resp.status_code
        try:
            utils.logError('yahoo get_data fail. ' + ticker + ' ' + str(code) + '. ' + str(resp.json()))
        except ValueError:
            utils.logError('yahoo get_data fail. ' + ticker + ' ' + str(code) + '.empty response')
        return []
        
    # get JSON response
    data = resp.json()
    data = data["chart"]["result"][0]

    if not is_valid_data(ticker, data):
        return []

    candles = data["indicators"]["quote"][0]
    candles.setdefault('timestamp', data["timestamp"])
    regularMarketTime = data['meta']['regularMarketTime']
    sessionStartTime = data['meta']['currentTradingPeriod']['pre']['start']
    sessionEndTime = data['meta']['currentTradingPeriod']['post']['end']

    result = []
    for i in range(len(candles['timestamp'])):
        data = []
        openTime = candles['timestamp'][i]
        closeTime = __getExpectedCloseTime(openTime, intervalStr)

        data.append(openTime)
        data.append(candles['open'][i])
        data.append(candles['high'][i])
        data.append(candles['low'][i])
        data.append(candles['close'][i])
        data.append(closeTime)
        if __isValidCandle(data, regularMarketTime, sessionStartTime, sessionEndTime):
            result.append(__parseResponse(data, intervalStr))
        else:
            break

    return result

def tickers_sp500(include_company_data = False):
    '''Downloads list of tickers currently listed in the S&P 500 '''
    # get list of all S&P 500 stocks
    sp500 = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")[0]

    if include_company_data:
        return sp500

    sp_tickers = sp500.Symbol.tolist()
    sp_tickers = sorted(sp_tickers)
    
    return sp_tickers

class NasdaqTier(IntEnum):
    GLOBAL_SELECT = 0,
    GLOBAL = 1,
    CAPITAL = 2,
    ANY = 3

def tickers_nasdaq(tier, include_company_data = False):
    
    '''Downloads list of tickers currently listed in the NASDAQ'''
    
    ftp = ftplib.FTP("ftp.nasdaqtrader.com")
    ftp.login()
    ftp.cwd("SymbolDirectory")
    
    r = io.BytesIO()
    ftp.retrbinary('RETR nasdaqlisted.txt', r.write)
    
    if include_company_data:
        r.seek(0)
        data = pd.read_csv(r, sep = "|")
        return data
    
    info = r.getvalue().decode()
    lines = info.splitlines()
    datas = [line.split("|") for line in lines[1:]]
    tickers = []
    
    for data in datas:
        tickerTier = data[2]
        if tier == NasdaqTier.GLOBAL_SELECT:
            if tickerTier == 'Q':
                tickers.append(data[0])
        elif tier == NasdaqTier.GLOBAL:
            if tickerTier == 'G':
                tickers.append(data[0])
        elif tier == NasdaqTier.CAPITAL:
            if tickerTier == 'S':
                tickers.append(data[0])
        else:
            tickers.append(data[0])

    ftp.close()    

    return tickers
   
def tickers_other(include_company_data = False):
    '''Downloads list of tickers currently listed in the "otherlisted.txt"
       file on "ftp.nasdaqtrader.com" '''
    ftp = ftplib.FTP("ftp.nasdaqtrader.com")
    ftp.login()
    ftp.cwd("SymbolDirectory")
    
    r = io.BytesIO()
    ftp.retrbinary('RETR otherlisted.txt', r.write)
    
    if include_company_data:
        r.seek(0)
        data = pd.read_csv(r, sep = "|")
        return data
    
    info = r.getvalue().decode()
    splits = info.split("|")    
    
    tickers = [x for x in splits if "\r\n" in x]
    tickers = [x.split("\r\n")[1] for x in tickers]
    tickers = [ticker for ticker in tickers if "File" not in ticker]        
    
    ftp.close()    

    return tickers
    
def tickers_dow(include_company_data = False):
    
    '''Downloads list of currently traded tickers on the Dow'''

    site = "https://en.wikipedia.org/wiki/Dow_Jones_Industrial_Average"
    
    table = pd.read_html(site, attrs = {"id":"constituents"})[0]
    
    if include_company_data:
        return table

    dow_tickers = sorted(table['Symbol'].tolist())
    
    return dow_tickers    
    