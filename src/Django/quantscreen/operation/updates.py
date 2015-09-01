import django
import os
os.environ["DJANGO_SETTINGS_MODULE"] = "quantscreen.local_settings"
django.setup()
from rank.models import PEGRank, DividendRank
from django.utils.decorators import method_decorator
from stock.models import StockMeta, FinancialReport, YahooQuotes, Treasuries
import logging
import numpy
from datetime import datetime, date
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
  
  #if eps is negative then pe means nothing use op-income(EBITDA) to replace earning
  if rank.currentQuarterPE > 0:
    epsDiluted = [report.epsDiluted for report in reports if report.epsDiluted]
    diff = numpy.diff(epsDiluted)
    epsDiluted = epsDiluted[1:]
    growth = numpy.divide(diff, epsDiluted)
    #average eps growth rate during last 6 quarters
    avgGrowth = numpy.average(growth)
  else:
    #for those negative stocks has negative EPS or zero EPS
    #Try use EBIDT to calculate the growth
    #Usually these kind of company a fast growing companies
    #Investors are betting on the future otherwise they won't succeed in IPO 
    EBITDAs = [report.opIncome for report in reports if report.opIncome]
    diff = numpy.diff(EBITDAs)
    EBITDAs = EBITDAs[1:]
    growth = numpy.divide(diff, EBITDAs)
    #TBD average Growth is not accurate for fast growing company
    avgGrowth = numpy.average(growth)
  
  #average
  rank.epsQuarterGrowth = avgGrowth
  rank.epsQuarterGrowthStd = numpy.std(growth)
  #negative growth measn PEG does not apply here
  
  #for those stock has high fluctuation rate, PEG does not apply
  if rank.epsQuarterGrowthStd > 1.0 or avgGrowth <= 0:
    rank.nextQuaterPE = None
    rank.PEGNextQuarter = None
    return
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
  
  if rank.currentAnnualPE > 0:
    epsDiluted = [report.epsDiluted for report in reports if report.epsDiluted]
    diff = numpy.diff(epsDiluted)
    epsDiluted = epsDiluted[1:]
    growth = numpy.divide(diff, epsDiluted)
    #average eps growth rate during last 5 years
    avgGrowth = numpy.average(growth)
  else:
    #for those negative stocks has negative EPS or zero EPS
    #Try use EBIDT to calculate the growth
    #Usually these kind of company a fast growing companies
    #Investors are betting on the future otherwise they won't succeed in IPO 
    EBITDAs = [report.opIncome for report in reports if report.opIncome]
    diff = numpy.diff(EBITDAs)
    EBITDAs = EBITDAs[1:]
    growth = numpy.divide(diff, EBITDAs)
    avgGrowth = numpy.average(growth)

  rank.epsAnnualGrowth = avgGrowth
  rank.epsAnnualGrowthStd = numpy.std(growth)
  
  #for those stock has high fluctuation rate, PEG does not apply
  #negative growth measn PEG does not apply here
  if rank.epsAnnualGrowth > 1.0 or avgGrowth <= 0:
    rank.nextYearPE = None
    rank.PEGNextAnnual = None
    return
  
  rank.nextYearPE = rank.currentAnnualPE / (1.0 + avgGrowth)
  rank.PEGNextAnnual = rank.nextYearPE / rank.epsAnnualGrowth;
  return

def updatePEGRank(stock):
  quotes = YahooQuotes.objects.filter(symbol=stock.symbol).\
                               order_by('tradeDate')[:1]
  if len(quotes) > 0:
    preClose = None
    for quote in quotes:
      if quote.previousClose:
        preClose = quote.previousClose
        break
    if preClose is None:
      return
  else:
    #No Yahoo Quotes found for this symbol
    log.warning("no Yahoo quotes found for %s" % stock.symbol)
    return

  try:
    rank = PEGRank.objects.get(updateTime=date.today(), stock__symbol=stock.symbol)
  except:
    print "Creating new PEGRank for %s" % stock.symbol
    rank = PEGRank(stock=stock)
    
  quarterPEG(stock, rank, preClose)
  annualPEG(stock, rank, preClose)
  
  #High PE means:
  #1.Overpriced (high growth estimate or irrational) 
  #2.earning decline (slow market)
  
  #low PE means:
  #1.Underpriced (low growth esitmate or irrational)
  #2.earning increase (slow market)
  
  rank.rate = 0.0
  
  if rank.PEGNextAnnual and rank.PEGNextQuarter:
    rank.rate = (rank.PEGNextAnnual + rank.PEGNextQuarter) / 2.0
  
  rank.save()   
  return 

def updateDividendRank(stock):
  quotes = YahooQuotes.objects.filter(symbol=stock.symbol).\
                               order_by('tradeDate')[:1]
  if len(quotes) > 0:
    preClose = None
    for quote in quotes:
      if quote.previousClose:
        preClose = quote.previousClose
        break
    if preClose is None:
      return
  else:
    #No Yahoo Quotes found for this symbol
    log.warning("no Yahoo quotes found for %s" % stock.symbol)
    return
  
  try:
    rank = DividendRank.objects.get(updateTime=date.today(), stock__symbol=stock.symbol)
  except:
    print "Creating new DividendRank for %s" % stock.symbol
    rank = DividendRank(stock=stock)
  
  reports = FinancialReport.objects.filter(symbol=stock.symbol,\
                                          docType='10-K').\
                                   order_by('-fiscalYear',\
                                            '-periodFocus')[:5]
                                            
  if len(reports) == 0:
    #No Annual Report found for this symbol
    log.warning("No Annual Report found for %s" % stock.symbol)
    return
  
  dividends = [report.dividend for report in reports]
  rank.stdAnnualDividend = numpy.std(dividends)
  if rank.stdAnnualDividend > 0.05:
    #if annual dividend vary a lot which means
    #1.ROA is growing or declining
    #2.ROA is unstable  
    x = numpy.arange(0, len(dividends), 1.0)
    z = numpy.polyfit(x, dividends, 1)
    #linear fitting shows it is growing
    
    if z[0] > 0.1:
      #use previous dividend as 
      rank.avgAnnualDividend = dividends[0]
    else:
      rank.avgAnnualDividend = numpy.average(dividends)  
  else:
    rank.avgAnnualDividend = numpy.average(dividends)
  
  rank.estAnnualReturn = rank.avgAnnualDividend / quote.previousClose; 
  
  #Overall return consist of two parts
  #1 Annual Dividend return
  #2 Annual price growth (assuming PE keeps the same, price growth equal to eps growth)
  #Only use the first for now
  rank.rate = rank.estAnnualReturn
  
  rank.save()
  return

if __name__ == "__main__":
  current = time.time()
  
  benchmarkRate = Treasuries.objects.all().order_by('-date')[:1]
  if len(benchmarkRate) > 0:
    rate = benchmarkRate[0].yields
    stopPE = 1.0 / rate
  else:
    log.warning("no treasuries data found")
  
  stocks = StockMeta.objects.all()
  for stock in stocks:
    updatePEGRank(stock)
    updateDividendRank(stock)
  print "Total Time", time.time() - current
