import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "quantscreen.local_settings") 
import django
django.setup()
from stock.models import YahooQuotes
import sys
import time
import re
import pandas
from datetime import datetime

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
      setattr(quote, name, date)
      continue
    val = expandMillion(row[name]) 
    setattr(quote, name, val)
    #print name, row[name], getattr(quote, name)

  quote.save(using='default')

if __name__ == "__main__":
  django.setup()
  data_path = sys.argv[1]
  
  current = time.time()
  
  quotes = pandas.read_csv(data_path)
  quotes = quotes.set_index('symbol')
  for s, row in quotes.iterrows():
    save(s, row)

  print "Total Time", time.time() - current
