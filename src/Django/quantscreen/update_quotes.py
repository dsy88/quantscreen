import pandas
from datetime import datetime
import urllib, urllib2
from io import StringIO
import sys
import re
import time
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "quantscreen.settings") 
import django
django.setup()
from stockquotes.models import YahooQuotes

YAHOO_URL = "http://finance.yahoo.com/d/quotes.csv"

def post(url, params):
  data = urllib.urlencode(params)
  response = urllib2.urlopen("%s?%s" % (url, data))
  #response = urllib2.urlopen("http://finance.yahoo.com/d/quotes.csv?s=TRUE&f=anp")
  return response.read()

def expandMillion(val):
  if type(val) is not type('str'):
    return val
  regex = '^[-+]?[0-9]*\.?[0-9]+M$'
  match = re.search(regex, val)
  if match:
    val = val.replace('M', '')
    val = float(val) * 1000000
    return val
  
  regex = '^[-+]?[0-9]*\.?[0-9]+B$'
  match = re.search(regex, val)
  if match:
    val = val.replace('B', '')
    val = float(val) * 1000000000
    return val

  return val

def save(symbol, row):
  print YahooQuotes.objects.count(), symbol
  quote = YahooQuotes()
  quote.symbol = symbol
  
  for name in vars(quote).keys():
    if name == 'symbol' or name == 'updateTime' or name.startswith('_') or name == 'id':
      continue
    if pandas.isnull(row[name]):
      setattr(quote, name, None)
      continue
    if name == 'TradeDate' or name == 'lastTradeDate' or name == 'dividendPayDate' \
       or name == 'exDividendDate':
      date = datetime.strptime(row[name], "%m/%d/%Y").strftime('%Y-%m-%d')
      print date
      setattr(quote, name, date)
      continue
    val = expandMillion(row[name]) 
    setattr(quote, name, val)
    print name, row[name], getattr(quote, name)

  quote.save(using='default')

def parse(symbols):
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
  content = post(YAHOO_URL, params) 
  content = content.decode('utf-8')
  quotes = pandas.read_csv(StringIO(content), names=columns, header=None)
  quotes = quotes.set_index('symbol')
  for s, row in quotes.iterrows():
    save(s, row)


def fetch(path, market):
  market = pandas.read_csv(path + "/" + market + ".csv", index_col=0)
  count = 0
  symbols = []
  for symbol, row in market.iterrows():
    if count < 90:
      symbols.append(symbol)
      count += 1
      continue
    parse(symbols)
    symbols = []
    count = 0
  
  if symbols:
    parse(symbols)

if __name__ == "__main__":
  django.setup()
  data_path = sys.argv[1]
  
  current = time.time()
  fetch(data_path, 'NASDAQ')
  fetch(data_path, 'NYSE')
  fetch(data_path, 'AMEX')
  print "Total Time", time.time() - current
