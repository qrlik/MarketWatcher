import requests
import pandas as pd
import ftplib
import io
import time
from enum import IntEnum
from datetime import datetime

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

def getExpectedCloseTime(openTime, interval):
    dt = datetime.fromtimestamp(openTime)
    if interval == '1d':
        if isWeekend(dt.isoweekday()):
            return None
        return openTime + __regularSession + __postSession
    elif interval == '1wk':
        weekday = dt.isoweekday()
        if isWeekend(weekday):
            return None
        return openTime + (5 - weekday) * __oneDay + __tradeSession
    elif interval == '1mo':
        lastWorkDay = dt.day
        day = dt.day + 1
        while True:
            try:
                nextDt = dt.replace(day=day)
                if not isWeekend(nextDt.isoweekday()):
                    lastWorkDay = day
                day += 1
            except Exception:
                return openTime + (lastWorkDay - dt.day) * __oneDay + __tradeSession
    else:
        raise AssertionError("invalid interval")

def isExpectNewCandles(openTime, interval):
    if interval not in ['1d', '1wk', '1mo']:
        raise AssertionError("invalid interval")
    openDt = datetime.fromtimestamp(openTime)
    lastTimestamp = openTime + 86400
    while True:
        dt = datetime.fromtimestamp(lastTimestamp)
        if interval == '1d' and not isWeekend(dt.isoweekday()) \
        or interval == '1wk' and dt.isoweekday() == Weekday.MONDAY \
        or interval == '1mo' and dt.month != openDt.month:
            closeTime = getExpectedCloseTime(lastTimestamp, interval)
            return closeTime < time.time()
        lastTimestamp = openTime + 86400

def isValidCandle(candle, regularMarketTime, sessionStartTime, sessionEndTime):
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
        x = 5
    return True
    

def build_url(ticker, start_date = None, end_date = None, interval = "1d"):
    if end_date is None:  
        end_seconds = int(pd.Timestamp("now").timestamp())
    else:
        end_seconds = int(pd.Timestamp(end_date).timestamp())
        
    if start_date is None:
        start_seconds = 7223400  
    else:
        start_seconds = int(pd.Timestamp(start_date).timestamp())
    
    site = base_url + ticker
    
    params = {"period1": start_seconds, "period2": end_seconds, "interval": interval.lower()} #, "events": "div,splits"}
    return site, params

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
        raise AssertionError("invalid interval")
    
    # build and connect to URL
    site, params = build_url(ticker, start_date, end_date, intervalStr)
    resp = requests.get(site, params = params, headers = headers)
    
    if not resp.ok:
        raise AssertionError(resp.json())
        
    # get JSON response
    data = resp.json()
    data = data["chart"]["result"][0]

    if data['meta']['currency'] != 'USD':
        print(ticker + ' wrong currency')
        return

    candles = data["indicators"]["quote"][0]
    candles.setdefault('timestamp', data["timestamp"])
    regularMarketTime = data['meta']['regularMarketTime']
    sessionStartTime = data['meta']['currentTradingPeriod']['pre']['start']
    sessionEndTime = data['meta']['currentTradingPeriod']['post']['end']

    amount = len(candles['timestamp'])
    if amount > 0 and candles['timestamp'][-1] == regularMarketTime:
        amount -= 1

    result = []
    for i in range(amount):
        candle = []
        openTime = candles['timestamp'][i]
        closeTime = getExpectedCloseTime(openTime, intervalStr)

        candle.append(openTime)
        candle.append(candles['open'][i])
        candle.append(candles['high'][i])
        candle.append(candles['low'][i])
        candle.append(candles['close'][i])
        candle.append(closeTime)
        if isValidCandle(candle, regularMarketTime, sessionStartTime, sessionEndTime):
            candle[0] *= 1000
            candle[1] = round(candle[2], 2)
            candle[2] = round(candle[3], 2)
            candle[3] = round(candle[4], 2)
            candle[4] = round(candle[5], 2)
            candle[5] *= 1000
            result.append(candle)
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

def tickers_nasdaq(include_company_data = False):
    
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
    splits = info.split("|")
    
    
    tickers = [x for x in splits if "\r\n" in x]
    tickers = [x.split("\r\n")[1] for x in tickers if "NASDAQ" not in x != "\r\n"]
    tickers = [ticker for ticker in tickers if "File" not in ticker]    
    
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
    