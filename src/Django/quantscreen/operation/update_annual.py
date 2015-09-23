import django
import os
os.environ["DJANGO_SETTINGS_MODULE"] = "quantscreen.local_settings"
django.setup()
from rank.models import Statistics, AnnualStatistics, DailyStatistics
from django.utils.decorators import method_decorator
from stock.models import StockMeta, FinancialReport, YahooQuotes, Treasuries, YahooHistory
import logging
import numpy
from datetime import datetime, date, timedelta
from django.views.decorators.csrf import csrf_exempt
import time

log=logging.getLogger('django')

def CalculateGrowth(stat, report, previousReport):
  if previousReport:
      if report.epsDiluted and previousReport.epsDiluted:
        stat.epsGrowth = (report.epsDiluted - previousReport.epsDiluted) / previousReport.epsDiluted
        stat.adjGrowth = stat.epsGrowth
      if report.netIncome and previousReport.netIncome:
        stat.netIncomeGrowth  = (report.netIncome - previousReport.netIncome) / previousReport.netIncome
        if not stat.adjGrowth:
          stat.adjGrowth = stat.netIncomeGrowth
      if previousReport.revenues and report.revenues:
        stat.revenueGrowth = (report.revenues - previousReport.revenues) / previousReport.revenues
        if not stat.adjGrowth:
          stat.adjGrowth = stat.revenueGrowth
  return

def CalculateDividend(stat, report):
  if report.dividend and report.epsDiluted:
    stat.payoutRate = report.dividend / report.epsDiluted
      
  if stat.ROE and stat.payoutRate:
    stat.expectedGrowthRate = stat.ROE * (1.0 - stat.payoutRate)
    stat.estimateDividend = report.dividend * (1.0 + stat.expectedGrowthRate)
  return

def UpdateStatistics(stock):
  reports = FinancialReport.objects.filter(stock__symbol=stock.symbol,\
                                          docType__in=['10-K', '20-F'],\
                                          annualStatistics__isnull=True).\
                                          order_by('fiscalYear')
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
      stat = AnnualStatistics.objects.get(stock__symbol=stock.symbol, fiscalYear=report.fiscalYear)
    except:
      stat = AnnualStatistics(stock=stock, fiscalYear=report.fiscalYear, report=report)
    else:
      previousReport = report
      continue
    
    if not report.curLiab:
      report.curLiab = 0.0
      
    if not report.equity:
      report.equity = 0.0
      
    if not report.curAssets:
      report.curAssets = 0.0
    
    if report.netIncome:
      investedCapital = (report.equity + report.curLiab - report.curAssets)
      if investedCapital > 0:
        stat.ROIC = report.netIncome / investedCapital
    
    if report.netIncome and report.assets:
      stat.ROA = report.netIncome / report.assets
      
    if report.netIncome and report.equity:
      stat.ROE = report.netIncome / report.equity
      
    quotes = YahooQuotes.objects.filter(stock__symbol=stock.symbol).order_by('-updateTime')
    if len(quotes) > 0:
      quote = quotes[0]
    else:
      quote = None
    if quote and quote.marketCapitalization:
      stat.EV = quote.marketCapitalization + report.curLiab - report.curAssets
    else:
      log.warning("No MarketCapitalizaiont found for %s" % stock.symbol)
      
    if quote and quote.EBITDA and stat.EV:
      stat.EVtoEBITDA = stat.EV / quote.EBITDA
      
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
