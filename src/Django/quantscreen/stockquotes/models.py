from django.db import models

# Create your models here.
class YahooQuotes(models.Model):
  #Price
  ask = models.FloatField()
  bid = models.FloatField()
  previousClose = models.FloatField()
  open = models.FloatField()  
     
  #Dividends
  dividendYield = models.FloatField()
  dividendPerShare = models.FloatField()
  dividendPayDate = models.DateField()
  exDividendDate = models.DateField()
  
  #Date
  tradeDate = models.DateField()
  lastTradeDate = models.DateField()
  lastTradeTime = models.DateTimeField()
  
  #Ratio
  earningPerShare = models.FloatField()
  EPSEstmateCurrentYear = models.FloatField()
  EPSEstimateNextYear = models.FloatField()
  EPSEstimateNextQuarter = models.FloatField()
  bookValue = models.FloatField()
  EBITDA = models.FloatField()
  priceSale = models.FloatField()
  priceBook = models.FloatField()
  pe = models.FloatField()
  peg = models.FloatField()
  peCurrentYear = models.FloatField()
  peNextYear = models.FloatField()
  shortRatio = models.FloatField()
  
  #Misc
  revenue = models.FloatField()
  holdingsValue = models.FloatField()
  dayValueChange = models.FloatField()
  holdingGainPercent = models.FloatField()
  annualizedGain = models.FloatField()
  holdingsGain = models.FloatField()
   
  #Volume
  askSize = models.FloatField()
  bidSize = models.FloatField()
  lastTradeSize = models.FloatField()
  averageDailyVolume = models.FloatField()
  
  #Symbol Info
  marketCapitalization = models.FloatField()
  floatShares = models.FloatField()
  name = models.CharField(max_length = 100)
  symbol = models.CharField(max_length = 100)
  sharesOwned = models.FloatField()
  stockExchange = models.CharField()
  sharesOutstanding = models.FloatField()
  
  #Averages
  commission = models.FloatField()
  oneYearTargetPrice = models.FloatField()
  
  
  
  