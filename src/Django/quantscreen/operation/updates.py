import django
import os
os.environ["DJANGO_SETTINGS_MODULE"] = "quantscreen.local_settings"
django.setup()
from rank.models import Statistics
from django.utils.decorators import method_decorator
from stock.models import StockMeta, FinancialReport, YahooQuotes, Treasuries
import logging
import numpy
from datetime import datetime, date
from django.views.decorators.csrf import csrf_exempt
import time

log=logging.getLogger('django')

def cleanDividends(dividends, preClose):
  ret = []
  for dividend in dividends:
    #unreasonable dividend  
    while dividend / preClose > 0.5:
      dividend /= 10.0
    ret.append(dividend)  
  
  return ret

def calculateGrowth(reports, stat):
  #if eps is negative then pe means nothing use op-income(EBITDA) to replace earning
  if stat.currentAnnualPE > 0:
    epsDiluted = [report.epsDiluted for report in reports if report.epsDiluted]
    diff = numpy.diff(epsDiluted)
    epsDiluted = epsDiluted[1:]
    growth = numpy.divide(diff, epsDiluted)
    #average eps growth rate during last 5 years

  else:
    #for those negative stocks has negative EPS or zero EPS
    #Try use EBIDT to calculate the growth
    #Usually these kind of company a fast growing companies
    #Investors are betting on the future otherwise they won't succeed in IPO 
    opIncomes = [report.opIncome for report in reports if report.opIncome]
    diff = numpy.diff(opIncomes)
    opIncomes = opIncomes[1:]
    #TBD average Growth is not accurate for fast growing company
    growth = numpy.divide(diff, opIncomes)
    
  avgGrowth = numpy.average(growth)
  avgGrowthStd = numpy.std(growth)
    
  return (avgGrowth, avgGrowthStd)

def calculateROIC(reports, stat):
  incomes = [report.netIncome for report in reports if report.netIncome]
  avgNetIncome = numpy.average(incomes)
  Equities = [report.equity for report in reports if report.equity]
  avgEquity = numpy.average(Equities)
  liabs = [report.curLiab for report in reports if report.curLiab]
  avgLiab = numpy.average(liabs)
  curAssets = [report.curAssets for report in reports if report.curAssets]
  avgCurAssets = numpy.average(curAssets)
  
  avgInvestedCapital = (avgEquity + avgLiab - avgCurAssets)
  if avgInvestedCapital > 0:
    return avgNetIncome / avgInvestedCapital
  else:
    return 0

def calculateROA(reports, stat):
  incomes = [report.netIncome for report in reports if report.netIncome]
  avgNetIncome = numpy.average(incomes)
  assets = [report.assets for report in reports if report.assets]
  avgAssets = numpy.average(assets)
  
  return avgNetIncome / avgAssets
  
def UpdateAnnual(stock, quote, stat):
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
      log.warning("No quarterly EPS found for %s" % stock.symbol)
      return
  else:
    #No Annual Report found for this symbol
    log.warning("No Annual Report found for %s" % stock.symbol)
    return
  
  #High PE means:
  #1.Overpriced (high growth estimate or irrational) 
  #2.earning decline (slow market)
  
  #low PE means:
  #1.Underpriced (low growth esitmate or irrational)
  #2.earning increase (slow market)  
  stat.currentAnnualPE = quote.previousClose / currentEPS
  
  (stat.epsAnnualGrowth, stat.epsAnnualGrowthStd) = calculateGrowth(reports, stat)
  
  #for those stock has high fluctuation rate, PEG does not apply
  #negative growth measn PEG does not apply here
  if stat.epsAnnualGrowth > 1.0 or stat.epsAnnualGrowth <= 0:
    stat.nextYearPE = None
    stat.PEGNextAnnual = None
    return
  
  stat.nextYearPE = stat.currentAnnualPE / (1.0 + stat.epsAnnualGrowth)
  stat.PEGNextAnnual = stat.nextYearPE / stat.epsAnnualGrowth;
  
  dividends = cleanDividends([report.dividend for report in reports], quote.previousClose)
  
  stat.stdAnnualDividend = numpy.std(dividends)
  if stat.stdAnnualDividend > 0.05:
    #if annual dividend vary a lot which means
    #1.ROA is growing or declining
    #2.ROA is unstable  
    x = numpy.arange(0, len(dividends), 1.0)
    z = numpy.polyfit(x, dividends, 1)
    #linear fitting shows it is growing
    
    if z[0] > 0.1:
      #use previous dividend as 
      stat.avgAnnualDividend = dividends[0]
    else:
      stat.avgAnnualDividend = numpy.average(dividends)  
  else:
    stat.avgAnnualDividend = numpy.average(dividends)
  
  stat.estAnnualReturn = stat.avgAnnualDividend / quote.previousClose; 
  
  #Overall return consist of two parts
  #1 Annual Dividend return
  #2 Annual price growth (assuming PE keeps the same, price growth equal to eps growth)
  #Only use the first for now

  #Only use equity and liability for now add cash TBD 
  if not reports[0].curLiab:
    reports[0].curLiab = 0.0
    
  if not reports[0].equity:
    reports[0].equity = 0.0
    
  if not reports[0].curAssets:
    reports[0].curAssets = 0.0 
   
  if reports[0].netIncome:
    investedCapital = (reports[0].equity + reports[0].curLiab - reports[0].curAssets)
    if investedCapital > 0:
      stat.currentAnnualROIC = reports[0].netIncome / investedCapital
  
  if stat.currentAnnualROIC is None:
    print  "stock %s has no ROIC" % stock.symbol
  
  stat.avgAnnualROIC = calculateROIC(reports, stat)
  
  if reports[0].netIncome and reports[0].assets:
    stat.currentAnnualROA = reports[0].netIncome / reports[0].assets
  stat.avgAnnualROA = calculateROA(reports, stat)
  
  if quote.marketCapitalization:
    stat.enterpriseValue = quote.marketCapitalization + reports[0].curLiab - reports[0].curAssets;
  else:
    log.warning("No MarketCapitalizaiont found for %s" % stock.symbol)
    
  if quote.EBITDA and stat.enterpriseValue:
    stat.EVtoEBITDA = stat.enterpriseValue / quote.EBITDA
  
  return

def UpdateQuarter(stock, quote, stat):
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
      log.warning("No quarterly EPS found for %s" % stock.symbol)
      return
  else:
    #No Quarterly Reports found for this symbol
    #This is the case for new IPO symbols, have to find other ways
    log.warning("No Quarterly Report found for %s" % stock.symbol)
    return
  
  stat.currentQuarterPE = quote.previousClose / currentEPS
  
  #average
  (stat.epsQuarterGrowth, stat.epsQuarterGrowthStd) = calculateGrowth(reports, stat)
  #negative growth measn PEG does not apply here
  
  #for those stock has high fluctuation rate, PEG does not apply
  if stat.epsQuarterGrowthStd > 1.0 or stat.epsQuarterGrowth <= 0:
    stat.nextQuaterPE = None
    stat.PEGNextQuarter = None
    return
  stat.nextQuaterPE = stat.currentQuarterPE / (1.0 + stat.epsQuarterGrowth);
  stat.PEGNextQuarter = stat.nextQuaterPE / stat.epsQuarterGrowth
  
  if not reports[0].curLiab:
    reports[0].curLiab = 0.0
    
  if not reports[0].equity:
    reports[0].equity = 0.0
    
  if not reports[0].curAssets:
    reports[0].curAssets = 0.0 
    
  if not reports[0].assets:
    reports[0].assets = 0.0
   
  
  if reports[0].netIncome:
    investedCapital = (reports[0].equity + reports[0].curLiab - reports[0].curAssets)
    if investedCapital > 0:
      stat.currentQuarterROIC = reports[0].netIncome / investedCapital
  
  stat.avgQuarterROIC = calculateROIC(reports, stat)
  
  if reports[0].netIncome and reports[0].assets:
    stat.currentQuarterROA = reports[0].netIncome / reports[0].assets
  stat.avgQuarterROA = calculateROA(reports, stat)
  
  return

def UpdateStatistics(stock):
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
    stat = Statistics.objects.get(updateTime=date.today(), stock__symbol=stock.symbol)
  except:
    print "Creating new Statistics for %s" % stock.symbol
    stat = Statistics(stock=stock)
    
  UpdateAnnual(stock, quotes[0], stat)
  UpdateQuarter(stock, quotes[0], stat)
  
  stat.save()
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
    UpdateStatistics(stock)
    
  print "Total Time", time.time() - current
