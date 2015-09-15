import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "quantscreen.local_settings") 
import django
django.setup()
from stock.models import YahooHistory, StockMeta
import sys
import time
import re
import pandas
from datetime import datetime

def save(symbol, stock, row):
  history = YahooHistory()
  history.stock = stock
  
  for name in vars(history).keys():
    if name == 'symbol' or name.startswith('_') or name == 'id' or name == "stock_id":
      continue
    if name == 'adjClose':
      val = row['adj close']
      setattr(history, name, val)
      continue
    
    if pandas.isnull(row[name]):
      setattr(history, name, None)
      continue

    val = row[name]
    setattr(history, name, val)
    #print name, row[name], getattr(quote, name)
  
  #print "imported", symbol
  history.save(using='default')

if __name__ == "__main__":
  django.setup()
  data_path = sys.argv[1]
  
  current = time.time()
  
  for parent,dirname,filenames in os.walk(data_path):
    for filename in filenames:        
      history = pandas.read_csv(parent + '/' +  filename)
      history = history.set_index('symbol')
      pre = None
      dates = []
      total = len(history)
      count = 0
      for s, row in history.iterrows():
        if s != pre:
          datas = YahooHistory.objects.filter(stock__symbol=s)
          dates = [data.date.strftime('%Y-%m-%d') for data in datas]    
          try:
            stock = StockMeta.objects.get(symbol=s)
          except Exception as e:
            print s, "Not Exists"
            continue
          pre = s
        if row['date'] in dates:
          print s, row['date'], "Exist"
          continue
        save(s, stock, row)
        percent = count * 100.0 / total
        if count % 10000 == 0:  
          print percent, "Percent"
        count += 1

  print "Total Time", time.time() - current
