import pandas
from datetime import datetime
import urllib, urllib2
from io import StringIO
import sys
import re
import time
import os

YAHOO_URL = "http://finance.yahoo.com/d/quotes.csv"

def post(url, params):
  data = urllib.urlencode(params)
  print url, data
  response = urllib2.urlopen("%s?%s" % (url, data))
  #response = urllib2.urlopen("http://finance.yahoo.com/d/quotes.csv?s=TRUE&f=anp")
  content = response.read()
  response.close()
  return content

def download(symbols):
  params = {}
  params['s'] = symbols
  params['f'] = 'sabpoydr1qd2d1t1ee7e8e9b4j4p5p6rr5r6r7s7s6v1w1g1g3g4a5b6k3a2j1f6ns1xj2c3t8'
  columns = ['symbol', 'ask', 'bid', 'previousClose', 'open', 'dividendYield', 'dividendPerShare',
               'dividendPayDate', 'exDividendDate', 'tradeDate', 'lastTradeDate', 'lastTradeTime',
               'earningPerShare', 'EPSEstimateCurrentYear', 'EPSEstimateNextYear', 'EPSEstimateNextQuarter',
               'bookValue', 'EBITDA', 'priceSale', 'priceBook', 'pe', 'peg', 'peCurrentYear', 'peNextYear',
               'shortRatio', 'revenue', 'holdingsValue', 'dayValueChange', 'holdingGainPercent', 'annualizedGain',
               'holdingsGain', 'askSize', 'bidSize', 'lastTradeSize', 'averageDailyVolume', 'marketCapitalization',
               'floatShares', 'name', 'sharesOwned', 'stockExchange', 'sharesOutstanding', 'commission', 'oneYearTargetPrice']
  
  while(True): 
    try:
      content = post(YAHOO_URL, params)
      break
    except:
      print "Failed to fetch, try again"
      
  content = content.decode('utf-8')
  if not os.path.exists('yahoo' + time.strftime("-%Y-%m-%d") +'.csv'):
    with open('yahoo' + time.strftime("-%Y-%m-%d") +'.csv', 'w') as f:
      for item in columns:
        f.write(item + ',')
      f.write('\n')
  with open('yahoo' + time.strftime("-%Y-%m-%d") +'.csv', 'a') as f:
    f.write(content)

def fetch(path, market):
  market = pandas.read_csv(path + "/" + market + ".csv", index_col=0)
  count = 0
  symbols = []
  for symbol, row in market.iterrows():
    if count < 90:
      symbols.append(symbol)
      count += 1
      continue
    download(symbols)
    symbols = []
    count = 0
  
  if symbols:
    download(symbols)

if __name__ == "__main__":
  data_path = sys.argv[1]
  
  current = time.time()
  fetch(data_path, 'NASDAQ')
  fetch(data_path, 'NYSE')
  fetch(data_path, 'AMEX')
  print "Total Time", time.time() - current
