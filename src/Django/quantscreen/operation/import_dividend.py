import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "quantscreen.local_settings") 
import django
django.setup()
from stock.models import DividendReport, StockMeta
import sys
import time
import re
import pandas
from datetime import datetime

def save(stock, row):
  dates = [datetime.strptime(row['declare_date'], "%B %d, %Y"),
           datetime.strptime(row['registration_date'], "%B %d, %Y"),
           datetime.strptime(row['pay_date'], "%B %d, %Y")]
  dates.sort()
  declareDate = dates[0]
  registrationDate = dates[1]
  payDate = dates[2]
  if DividendReport.objects.filter(stock=stock, payDate=payDate).exists():
    print "DividendReport of %s declared on %s exists " % (stock.symbol, declareDate)
    return False
  
  report = DividendReport(stock=stock)
  report.declareDate = declareDate
  report.registrationDate = registrationDate
  report.payDate = payDate
  
  dividend = row['dividend']
  
  try:
    dividend = float(dividend)
  except:
    m2 = re.match('(\d*\.?\d*)\s*(\w*)', dividend)
    if m2:
      dividend = float(m2.group(1))
      if 'cent' in m2.group(2).lower():
        dividend /= 100
    else:
      print "can't recognize dividend %s" % dividend
      return False 
  
  report.dividend = dividend
  report.reportURL = row['report_url']
  report.save()
  return True

if __name__ == "__main__":
  django.setup()
  data_path = sys.argv[1]
  
  current = time.time()
  DividendReport.objects.all().delete()
  for parent,dirname,filenames in os.walk(data_path):
    for filename in filenames:        
      dividends = pandas.read_csv(parent + '/' +  filename)
      dividends.set_index("symbol")
      for symbol, row in dividends.iterrows():  
        try:
          stock = StockMeta.objects.get(symbol=symbol)
        except Exception as e:
          print symbol, "symbol Not Exists"
          continue
      
        print "saving", stock.symbol
        save(stock, row)
          
  print "Total Time", time.time() - current
