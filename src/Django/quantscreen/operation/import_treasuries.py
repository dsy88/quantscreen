import django
django.setup()
import pandas
from datetime import datetime
import urllib, urllib2
from io import StringIO
import sys
import re
import time
from stock.models import *

def import_treasuries(path):
  data = pandas.read_csv(path, index_col=0)
  for date, row in data.iterrows():
    if Treasuries.objects.filter(date=date).exists():
      print date
      continue
    
    for key, value in row.iteritems():
      if key == 'date' or key == 'tid':
        continue
      if pandas.isnull(value):
        continue
      treasuries = Treasuries()
      treasuries.date = date
      treasuries.type = key
      treasuries.yields = value
      treasuries.save()
      
if __name__ == "__main__":
  django.setup()
  data_path = sys.argv[1]
  
  current = time.time()
  import_treasuries(data_path)
  print "Total Time", time.time() - current