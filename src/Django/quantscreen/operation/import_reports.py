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

def import_report(path):
  data = pandas.read_csv(path, index_col=0)
  for symbol, row in data.iterrows():
    symbol = symbol
    if FinancialReport.objects.filter(symbol=symbol, fiscalYear=row['fiscal_year'],\
                                      periodFocus=row['period_focus']).exists():
      print symbol, "exist"
      continue
    try:
      stock = StockMeta.objects.get(symbol=symbol)
    except Exception as e:
      print symbol
      continue
    
    report = FinancialReport()
    report.symbol = symbol
    report.endDate = row['end_date']
    report.amend = row['amend']
    report.periodFocus = row['period_focus'].strip()
    report.fiscalYear = row['fiscal_year'].strip()
    report.docType = row['doc_type'].strip()
    report.revenues = row['revenues']
    report.opIncome = row['op_income']
    report.netIncome = row['net_income']
    report.epsBasic = row['eps_basic']
    report.epsDiluted = row['eps_diluted']
    report.dividend = row['dividend']
    report.assets = row['assets']
    report.curAssets = row['cur_assets']
    report.curLiab = row['cur_liab']
    report.cash = row['cash']
    report.equity = row['equity']
    report.cashFlowOp = row['cash_flow_op']
    report.cashFlowInv = row['cash_flow_inv']
    report.cashFlowFin = row['cash_flow_fin']
    report.save()

if __name__ == "__main__":
  django.setup()
  data_path = sys.argv[1]
  
  current = time.time()
  import_report(data_path)
  print "Total Time", time.time() - current