import pandas
from datetime import datetime
import urllib, urllib2
from io import StringIO
import sys
import re
import time
import django
django.setup()
from stock.models import StockMeta

def import_meta(path, market):
  data = pandas.read_csv(path, index_col=0)
  for symbol, row in data.iterrows():
    if StockMeta.objects.filter(symbol=symbol).exists():
      print symbol, "exist"
      continue
    print "inserting", symbol
    meta = StockMeta()
    meta.symbol = symbol.strip()
    meta.market = market.strip()
    meta.name = row['Name'].strip()
    meta.IPOYear = row['IPOyear'].strip()
    meta.sector = row['Sector'].strip()
    meta.industry = row['industry'].strip()
    meta.summaryQuote = row['Summary Quote'].strip()
    meta.save()

if __name__ == "__main__":
  django.setup()
  data_path = sys.argv[1]
  market = sys.argv[2]
  
  current = time.time()
  import_meta(data_path, market)
  print "Total Time", time.time() - current