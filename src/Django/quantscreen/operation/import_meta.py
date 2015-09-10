import pandas
from datetime import datetime
import urllib, urllib2
from io import StringIO
import sys
import re
import time
import os
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
    if not pandas.isnull(row['Name']):
      meta.name = row['Name'].strip()
    if not pandas.isnull(row['IPOyear']):
      meta.IPOYear = row['IPOyear']
    if not pandas.isnull(row['Sector']):
      meta.sector = row['Sector'].strip()
    if not pandas.isnull(row['industry']):
      meta.industry = row['industry'].strip()
    if not pandas.isnull(row['Summary Quote']):
      meta.summaryQuote = row['Summary Quote'].strip()
    meta.save()

if __name__ == "__main__":
  django.setup()
  data_path = sys.argv[1]
  
  for parent,dirname,filenames in os.walk(data_path):
    for filename in filenames:
      market = filename.split('.')[0]
      current = time.time()
      import_meta(parent + '/' + filename, market)
      print "Used %f to import market %s" % (time.time() - current, market)