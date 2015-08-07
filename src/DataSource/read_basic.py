import pandas
from bs4 import BeautifulSoup
import urllib, urllib2
from io import StringIO
import sys

YAHOO_URL = "http://finance.yahoo.com/d/quotes.csv"

def post(url, params):
  data = urllib.urlencode(params)
  response = urllib2.urlopen("%s?%s" % (url, data))
  #response = urllib2.urlopen("http://finance.yahoo.com/d/quotes.csv?s=TRUE&f=anp")
  return response.read()

def eps(quote):
  if quote.earningsshare.string is None:
    return None

  return float(quote.earningsshare.string)

def peCurrentYear(quote):
  if quote.priceepsestimatecurrentyear.string is None:
    return None
 
  return float(quote.priceepsestimatecurrentyear.string)


if __name__ == "__main__":
  data_path = sys.argv[1]
  basic = pandas.read_csv(data_path + "/NASDAQ.csv", index_col=0)
  for symbol, row in basic.iterrows():
    print 'symbol:', symbol
    params = {}
    params['s'] = symbol
    params['f'] = "sperr5j4e7e8e9r6r7"

    content = post(YAHOO_URL, params) 
    content = content.decode('utf-8')
    quotes = pandas.read_csv(StringIO(content), index_col=0, header=None)
    for s, row in quotes.iterrows():
      print s,row.iget(5), row.iget(6),row.iget(7),row.iget(8), row.iget(9)
      #for price, earning, pe in row.iteritems():
        #print s,price,earning,pe 
