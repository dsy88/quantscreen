from django.db import models
from quantscreen.helper import JsonMethod
# Create your models here.

class Treasuries(models.Model):
  date = models.DateTimeField()
  type = models.CharField(max_length=50)
  yields = models.FloatField()
   
class StockMeta(models.Model, JsonMethod):
  symbol = models.CharField(max_length=100)
  name = models.CharField(max_length=500)
  market = models.CharField(max_length=100)
  IPOYear = models.CharField(max_length=10)
  sector = models.CharField(max_length=100)
  industry = models.CharField(max_length=100)
  summaryQuote = models.URLField()
  
  updateTime = models.DateTimeField(auto_now_add=True)
  
  
class FinancialReport(models.Model):
  symbol = models.CharField(max_length=100)
  endDate = models.DateField(null=True)
  amend = models.BooleanField()
  periodFocus = models.CharField(max_length=10)
  fiscalYear = models.CharField(max_length=10)
  #10-K, 10-Q
  docType = models.CharField(max_length=10)
  revenues = models.FloatField(null=True)
  opIncome = models.FloatField(null=True)
  netIncome = models.FloatField(null=True)
  epsBasic = models.FloatField(null=True)
  epsDiluted = models.FloatField(null=True)
  dividend = models.FloatField(null=True)
  assets = models.FloatField(null=True)
  curAssets = models.FloatField(null=True)
  curLiab = models.FloatField(null=True)
  cash = models.FloatField(null=True)
  equity = models.FloatField(null=True)
  cashFlowOp = models.FloatField(null=True)
  cashFlowInv = models.FloatField(null=True)
  cashFlowFin = models.FloatField(null=True)
  
  updateTime = models.DateTimeField(auto_now_add=True)
  
class YahooQuotes(models.Model, JsonMethod):
  #Price
  ask = models.FloatField(null=True)
  bid = models.FloatField(null=True)
  previousClose = models.FloatField(null=True)
  open = models.FloatField(null=True)  
     
  #Dividends
  dividendYield = models.FloatField(null=True)
  dividendPerShare = models.FloatField(null=True)
  dividendPayDate = models.DateField(null=True)
  exDividendDate = models.DateField(null=True)
  
  #Date
  tradeDate = models.DateField(null=True)
  lastTradeDate = models.DateField(null=True)
  lastTradeTime = models.TimeField(null=True)
  
  #Ratio
  earningPerShare = models.FloatField(null=True)
  EPSEstimateCurrentYear = models.FloatField(null=True)
  EPSEstimateNextYear = models.FloatField(null=True)
  EPSEstimateNextQuarter = models.FloatField(null=True)
  bookValue = models.FloatField(null=True)
  EBITDA = models.FloatField(null=True)
  priceSale = models.FloatField(null=True)
  priceBook = models.FloatField(null=True)
  pe = models.FloatField(null=True)
  peg = models.FloatField(null=True)
  peCurrentYear = models.FloatField(null=True)
  peNextYear = models.FloatField(null=True)
  shortRatio = models.FloatField(null=True)
  
  #Misc
  revenue = models.FloatField(null=True)
  holdingsValue = models.FloatField(null=True)
  dayValueChange = models.FloatField(null=True)
  holdingGainPercent = models.FloatField(null=True)
  annualizedGain = models.FloatField(null=True)
  holdingsGain = models.FloatField(null=True)
   
  #Volume
  askSize = models.FloatField(null=True)
  bidSize = models.FloatField(null=True)
  lastTradeSize = models.FloatField(null=True)
  averageDailyVolume = models.FloatField(null=True)
  
  #Symbol Info
  marketCapitalization = models.FloatField(null=True)
  floatShares = models.FloatField(null=True)
  name = models.CharField(max_length = 100, null=True)
  symbol = models.CharField(max_length = 100)
  sharesOwned = models.FloatField(null=True)
  stockExchange = models.CharField(null=True, max_length = 100)
  sharesOutstanding = models.FloatField(null=True)
  
  #Averages
  commission = models.FloatField(null=True)
  oneYearTargetPrice = models.FloatField(null=True)
  
  updateTime = models.DateTimeField(auto_now_add=True)
