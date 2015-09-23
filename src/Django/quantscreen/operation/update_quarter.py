import django
import os
from operation.update_annual import CalculateGrowth, CalculateDividend
os.environ["DJANGO_SETTINGS_MODULE"] = "quantscreen.local_settings"
django.setup()
from rank.models import Statistics, QuarterStatistics
from django.utils.decorators import method_decorator
from stock.models import StockMeta, FinancialReport, YahooQuotes, Treasuries, YahooHistory
import logging
import numpy
from datetime import datetime, date, timedelta
from django.views.decorators.csrf import csrf_exempt
import time

log=logging.getLogger('django')

def UpdateStatistics(stock):
  reports = FinancialReport.objects.filter(stock__symbol=stock.symbol,\
                                          docType__in=['10-Q'],\
                                          quarterStatistics__isnull=True).\
                                          order_by('fiscalYear', 'periodFocus')
                                          #distinct('fiscalYear')
                                          
  if len(reports) == 0:
    #No Annual Report found for this symbol
    log.warning("No Annual Report found for %s" % stock.symbol)
    return
  
  previousReport = None
  for report in reports:
    if previousReport and report.fiscalYear == previousReport.fiscalYear:
      continue
    try:
      stat = QuarterStatistics.objects.get(stock__symbol=stock.symbol, \
                                           fiscalYear=report.fiscalYear, \
                                           periodFocus=report.periodFocus)
    except:
      stat = QuarterStatistics(stock=stock, fiscalYear=report.fiscalYear, \
                               periodFocus=report.periodFocus, report=report)
    else:
      previousReport = report
      continue
    
    #ROE by quarter
    if report.netIncome and report.equity:
      stat.ROE = report.netIncome / report.equity
    
    CalculateDividend(stat, report)
    CalculateGrowth(stat, report, previousReport)
    stat.save()
    previousReport = report
  return

if __name__ == "__main__":
  current = time.time()
  
  stocks = StockMeta.objects.all()
  for stock in stocks:
    UpdateStatistics(stock)
    
  print "Total Time", time.time() - current
