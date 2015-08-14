import django
django.setup()
from rank.models import PEGRank
from django.utils.decorators import method_decorator
from stock.models import StockMeta, FinancialReport, YahooQuotes, Treasuries
import logging
import numpy
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
import time

log=logging.getLogger('django')

def quarterPEG(stock, rank, preClose):
  reports = FinancialReport.objects.filter(symbol=stock.symbol,\
                                         docType='10-Q').\
                                   order_by('-fiscalYear',\
                                            '-periodFocus')[:6]
                                            
  if len(reports) > 0:
    currentEPS = None
    for report in reports:
      if report.epsDiluted is not None:
        currentEPS = report.epsDiluted
        break
    #No historic quarterly EPS data available
    if currentEPS is None or currentEPS == 0.0:
      log.warn("No quarterly EPS found for %s" % stock.symbol)
      return
  else:
    #No Quarterly Reports found for this symbol
    #This is the case for new IPO symbols, have to find other ways
    log.warning("No Quarterly Report found for %s" % stock.symbol)
    return
  
  rank.currentQuarterPE = preClose/currentEPS
    
  epsDiluted = [report.epsDiluted for report in reports if report.epsDiluted]
  diff = numpy.diff(epsDiluted)
  epsDiluted = epsDiluted[1:]
  growth = numpy.divide(diff, epsDiluted)
  
  #average eps growth rate during last 12 quaters
  
  #TBD average Growth is not accurate for fast growing company
  avgGrowth = numpy.average(growth)
  
  #average
  rank.epsQuarterGrowth = avgGrowth
  rank.epsQuarterGrowthStd = numpy.std(growth)
  rank.nextQuaterPE = rank.currentQuarterPE / (1.0 + avgGrowth);
  rank.PEGNextQuarter = rank.nextQuaterPE / rank.epsQuarterGrowth
  return

def annualPEG(stock, rank, preClose):          
  reports = FinancialReport.objects.filter(symbol=stock.symbol,\
                                          docType='10-K').\
                                   order_by('-fiscalYear',\
                                            '-periodFocus')[:5]
                                            
  if len(reports) > 0:
    currentEPS = None
    for report in reports:
      if report.epsDiluted is not None:
        currentEPS = report.epsDiluted
        break
    #No historic quarterly EPS data available
    if currentEPS is None or currentEPS == 0.0:
      log.warn("No quarterly EPS found for %s" % stock.symbol)
      return
  else:
    #No Annual Report found for this symbol
    log.warning("No Annual Report found for %s" % stock.symbol)
    return
  
  rank.currentAnnualPE = preClose / currentEPS
  
  #TBD for those negative stocks has negative EPS or zero EPS
  #Try use revenue to calculate the growth
  
  epsDiluted = [report.epsDiluted for report in reports if report.epsDiluted]
  diff = numpy.diff(epsDiluted)
  epsDiluted = epsDiluted[1:]
  growth = numpy.divide(diff, epsDiluted)
  #average eps growth rate during last 5 years
  avgGrowth = numpy.average(growth)
  
  rank.epsAnnualGrowth = avgGrowth
  rank.epsAnnualGrowthStd = numpy.std(growth)
  rank.nextYearPE = rank.currentAnnualPE / (1.0 + avgGrowth)
  rank.PEGNextAnnual = rank.nextYearPE / rank.epsAnnualGrowth;
  return

def updatePEGRank():
  benchmarkRate = Treasuries.objects.all().order_by('-date')[:1]
  if len(benchmarkRate) > 0:
    rate = benchmarkRate[0].yields
  else:
    log.warning("no treasuries data found")
    return 
  
  stopPE = 1.0 / rate
  
  stocks = StockMeta.objects.all()
  for stock in stocks:
    quotes = YahooQuotes.objects.filter(symbol=stock.symbol).\
                                 order_by('tradeDate')[:1]
    if len(quotes) > 0:
      preClose = None
      for quote in quotes:
        if quote.previousClose:
          preClose = quote.previousClose
          break
      if preClose is None:
        continue
    else:
      #No Yahoo Quotes found for this symbol
      log.warning("no Yahoo quotes found for %s" % stock.symbol)
      continue

    rank = PEGRank(stock=stock)
    rank.save()

    quarterPEG(stock, rank, preClose)
    annualPEG(stock, rank, preClose)
    
    #High PE means:
    #1.Overpriced (high growth estimate or irrational) 
    #2.earning decline (slow market)
    
    #low PE means:
    #1.Underpriced (low growth esitmate or irrational)
    #2.earning increase (slow market)
    
    if rank.PEGNextAnnual and rank.PEGNextQuarter:
      rank.rate = (rank.PEGNextAnnual + rank.PEGNextQuarter) / 2.0
    elif rank.PEGNextAnnual:
      rank.rate = rank.PEGNextAnnual
    elif rank.PEGNextQuarter:
      rank.rate = rank.PEGNextQuarter
    
    rank.save()
    
  return 


if __name__ == "__main__":
  django.setup()
  current = time.time()
  updatePEGRank()
  print "Total Time", time.time() - current
