import django
import os
os.environ["DJANGO_SETTINGS_MODULE"] = "quantscreen.local_settings"
django.setup()
from rank.models import DailyStatistics, AnnualStatistics, QuarterStatistics
from django.utils.decorators import method_decorator
from stock.models import StockMeta, FinancialReport, YahooQuotes, Treasuries, YahooHistory
import logging
import numpy
from datetime import datetime, date, timedelta
from django.views.decorators.csrf import csrf_exempt
import time

log=logging.getLogger('django')

def Beta(stock, stat, returns, marketReturns, lastDate):  
  minLen = len(returns)
  
  days = (lastDate - stat.date).days
  if days > 0:
    marketReturns = marketReturns[-minLen:-days]
  elif days == 0:
    marketReturns = marketReturns[-minLen:]
  else:
    log.warning('Benchmark can\'t match')
    return
  try:
    cov = numpy.cov(returns[-minLen:], marketReturns[-minLen:])[0][1]
  except:
    return None
  return cov / numpy.var(marketReturns)

def UpdateStatic(stock, stat, riskFreeReturnRate, marketReturnRate, returns, marketReturns, lastDate):
  stat.beta = Beta(stock, stat, returns, marketReturns, lastDate)
  
  if stat.beta:
    stat.equityReturnRate = riskFreeReturnRate + stat.beta * (marketReturnRate - riskFreeReturnRate)

  return

def RiskFreeReturnRate():
  benchmarkRate = Treasuries.objects.all().order_by('-date')[:1]
  if len(benchmarkRate) > 0:
    riskFreeReturnRate = benchmarkRate[0].yields
  else:
    log.warning("no treasuries data found")
    
  return riskFreeReturnRate

def MarketReturnRate():
  years = range(1990, 2015)
  
  benchmarks = []
  for year in years:
    benchmark = YahooHistory.objects.filter(stock__symbol="^GSPC", date__year=year).order_by('date')[0]
    benchmarks.append(benchmark.adjClose)
    
  benchmarkDiffs = numpy.diff(benchmarks)
  benchmarks = benchmarks[:-1]
  marketReturns = numpy.divide(benchmarkDiffs, benchmarks)
  avgMarketReturn = numpy.average(marketReturns)
  
  return avgMarketReturn

def UpdateStatistics(stock, riskFreeReturnRate, marketReturnRate, marketReturns, lastDate):
  
  historys = YahooHistory.objects.filter(stock__symbol=stock.symbol).\
                               order_by('-date')
  if len(historys) == 0:
    #No Yahoo Quotes found for this symbol
    log.warning("no Yahoo quotes found for %s" % stock.symbol)
    return
  
  close = [history.adjClose for history in historys]
  close.reverse()
  diff = numpy.diff(close)
  close = close[:-1]
  returns = numpy.divide(diff, close)
  
  for history in historys:
    try:
      stat = DailyStatistics.objects.get(date=history.date, stock__symbol=stock.symbol)
    except:
      print "Creating new DailyStatistics for %s" % stock.symbol
      stat = DailyStatistics(stock=stock)
    else:
      break
    
    stat.date = history.date
    stat.yahooHistory = history
    
    quotes = YahooQuotes.objects.filter(stock__symbol=stock.symbol, lastTradeDate=stat.date)
    if len(quotes) > 0:
      quote = quotes[0]
    else:
      quote = None
    if quote:
      stat.yahooQuote = quote
    
    UpdateStatic(stock, stat, riskFreeReturnRate, marketReturnRate, returns, marketReturns, lastDate)
    
    annualStats = AnnualStatistics.objects.filter(stock__symbol=stock.symbol).order_by('-fiscalYear')
    if len(annualStats) > 0:
      annualStat = annualStats[0]
    else:
      annualStat = None
      
    if not annualStat:
      log.warning("No Annual Stat found, update Annual stat first")
        
      if stat.yahooQuote:
        stat.annualPE = stat.yahooQuote.pe
    else:
      if int(annualStat.fiscalYear) <> stat.date.year - 1:
        log.warning("Last year Stat not found for %s" % stock.symbol)
        
      report = annualStat.report
      if report and report.epsDiluted:
        stat.annualPE = history.adjClose / report.epsDiluted
      else:
        log.warning("No Annual Report and yahoo Quotes found for %s" % stock.symbol)  
      
      if annualStat.adjGrowth > riskFreeReturnRate:
        if stat.annualPE > 0:
          stat.annualPEG = stat.annualPE / annualStat.adjGrowth
    
    quarterStats = QuarterStatistics.objects.filter(stock__symbol=stock.symbol).order_by('-fiscalYear', '-periodFocus')
    if len(quarterStats) > 0:
      quarterStat = quarterStats[0]
    else:
      quarterStat = None
      
    if not quarterStat:
      log.warning("No Quarter Stat found, update Quarter stat first")
      if stat.yahooQuote:
        stat.quarterPE = stat.yahooQuote.pe
    else:    
      report = quarterStat.report
      if report and report.epsDiluted:
        stat.quarterPE = history.adjClose / report.epsDiluted
      else:
        log.warning("No Quarter Report and yahoo Quotes found for %s" % stock.symbol)  
      
      if quarterStat.adjGrowth > riskFreeReturnRate:
        if stat.quarterPE > 0:
          stat.quarterPEG  = stat.quarterPE / quarterStat.adjGrowth
        
    stat.save()
    break
    returns = returns[:-1]
  return

if __name__ == "__main__":
  current = time.time()  
  
  stocks = StockMeta.objects.all()
  
    #Benchmark     
  benchmarks = YahooHistory.objects.filter(stock__symbol="^GSPC").order_by('date')
  lastDate = benchmarks[len(benchmarks)-1].date
  benchmarkClose = [benchmark.adjClose for benchmark in benchmarks]
  benchmarkDiff = numpy.diff(benchmarkClose)
  benchmarkClose = benchmarkClose[:-1]
  marketReturns = numpy.divide(benchmarkDiff, benchmarkClose)
  
  riskFreeReturnRate = RiskFreeReturnRate()
  marketReturnRate = MarketReturnRate()
  for stock in stocks:
    start = time.time()  
    if stock.symbol in ['^GSPC', '^DJI', '^IXIC']:
      continue
    UpdateStatistics(stock, riskFreeReturnRate, marketReturnRate, marketReturns, lastDate)
    print "Total Time %f for %s" % (time.time() - start, stock.symbol)
  print "Total Time", time.time() - current
