import pandas
from datetime import datetime
import urllib, urllib2
from io import StringIO
import sys
import re
import time
import os

YAHOO_URL = "http://ichart.yahoo.com/table.csv"

def post(url, params):
  data = urllib.urlencode(params)
  print url, data
  response = urllib2.urlopen("%s?%s" % (url, data))
  #response = urllib2.urlopen("http://finance.yahoo.com/d/quotes.csv?s=TRUE&f=anp")
  content = response.read()
  response.close()
  return content

def download(symbol, start_date):
  start = time.strptime(start_date, "%Y-%m-%d")
  params = {}
  params['s'] = symbol
  params['a'] = start.tm_mon - 1
  params['b'] = start.tm_mday
  params['c'] = start.tm_year
  params['d'] = int(time.strftime("%m")) - 1
  params['e'] = time.strftime("%d")
  params['f'] = time.strftime("%Y")
  params['g'] = 'd'
  try:
    content = post(YAHOO_URL, params)
  except:
    print "Failed to fetch %s" % symbol
    return
     
  content = content.decode('utf-8')
  lines = content.splitlines(True)
  if not os.path.exists('history-' + start_date +'.csv'):
    with open('history-' + start_date +'.csv', 'w') as f:
      f.write('symbol,')
      f.write(lines[0].lower())
  with open('history-' + start_date +'.csv', 'a') as f:
    for line in lines[1:]:
      f.write(symbol + ",")
      f.write(line)

def fetch(path, market, start_date):
  market = pandas.read_csv(path + "/" + market + ".csv", index_col=0)
  
  for symbol, row in market.iterrows():
    download(symbol, start_date)
  
  
if __name__ == "__main__":
  data_path = sys.argv[1]
  start_date = sys.argv[2]
  
  current = time.time()
  fetch(data_path, 'NASDAQ', start_date)
  fetch(data_path, 'NYSE', start_date)
  fetch(data_path, 'AMEX', start_date)
  fetch(data_path, 'INDEX', start_date)
  print "Total Time", time.time() - current
