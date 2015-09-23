from django.db import models
from stock.models import StockMeta, YahooQuotes, YahooHistory, FinancialReport
from django.db.models.lookups import StartsWith
from quantscreen.helper import JsonMethod

class DailyStatistics(models.Model, JsonMethod):
  stock = models.ForeignKey(StockMeta, 
                               related_name='dailyStatistics')
  yahooQuote = models.OneToOneField(YahooQuotes, related_name='dailyStatistics', null=True)
  yahooHistory = models.OneToOneField(YahooHistory, related_name='dailyStatistics', null=True)
  
  beta = models.FloatField(null=True)
  annualPE = models.FloatField(null=True)
  quarterPE = models.FloatField(null=True)
  estimateAnnualPE = models.FloatField(null=True)
  estimateQuarterPE = models.FloatField(null=True)
  
  annualPEG = models.FloatField(null=True)
  quarterPEG = models.FloatField(null=True)
  estimateAnnualPEG = models.FloatField(null=True)
  estimateQuarterPEG = models.FloatField(null=True)
  
  date = models.DateField()
  updateTime = models.DateField(auto_now_add=True)
  
class QuarterStatistics(models.Model, JsonMethod):
  stock = models.ForeignKey(StockMeta, 
                               related_name='quarterStatistics')
  report = models.OneToOneField(FinancialReport, related_name='quarterStatistics')
  
  periodFocus = models.CharField(max_length=10)
  fiscalYear = models.CharField(max_length=10)
  
  epsGrowth = models.FloatField(null=True)
  revenueGrowth = models.FloatField(null=True)
  netIncomeGrowth = models.FloatField(null=True)
  adjGrowth = models.FloatField(null=True)
  
  payoutRate = models.FloatField(null=True)
  expectedGrowthRate = models.FloatField(null=True)
  estimateDividend = models.FloatField(null=True)
  
  ROE = models.FloatField(null=True)
  
  updateTime = models.DateField(auto_now_add=True)

class AnnualStatistics(models.Model, JsonMethod):
  stock = models.ForeignKey(StockMeta, 
                               related_name='annualStatistics')
  report = models.OneToOneField(FinancialReport, related_name='annualStatistics')
  
  fiscalYear = models.CharField(max_length=10)
  epsGrowth = models.FloatField(null=True)
  revenueGrowth = models.FloatField(null=True)
  netIncomeGrowth = models.FloatField(null=True)
  adjGrowth = models.FloatField(null=True)
  
  ROIC = models.FloatField(null=True)
  ROA = models.FloatField(null=True)
  ROE = models.FloatField(null=True)
  EV = models.FloatField(null=True)
  EVtoEBITDA = models.FloatField(null=True)
  
  payoutRate = models.FloatField(null=True)
  expectedGrowthRate = models.FloatField(null=True)
  estimateDividend = models.FloatField(null=True)
  
  updateTime = models.DateField(auto_now_add=True)
  


class Statistics(models.Model, JsonMethod):
  stock = models.ForeignKey(StockMeta, 
                               related_name='statistics')
  #Growth and PE
  currentAnnualPE = models.FloatField(null=True)
  currentQuarterPE = models.FloatField(null=True)
  nextQuaterPE = models.FloatField(null=True)
  nextYearPE = models.FloatField(null=True)
  
  epsQuarterGrowthStd = models.FloatField(null=True)
  epsAnnualGrowthStd = models.FloatField(null=True)
  epsQuarterGrowth = models.FloatField(null=True)
  epsAnnualGrowth = models.FloatField(null=True)
  
  revenueQuarterGrowthStd = models.FloatField(null=True)
  revenueAnnualGrowthStd = models.FloatField(null=True)
  revenueQuarterGrowth = models.FloatField(null=True)
  revenueAnnualGrowth= models.FloatField(null=True)
  
  EBIDTQuarterGrowthStd = models.FloatField(null=True)
  EBIDTAnnualGrowthStd = models.FloatField(null=True)
  EBIDTQuarterGrowth = models.FloatField(null=True)
  EBIDTAnnualGrowth = models.FloatField(null=True)
  
  PEGNextQuarter = models.FloatField(null=True)
  PEGNextAnnual = models.FloatField(null=True)
  
  QuarterTargetPrice = models.FloatField(null=True)
  AnnualTargePrice = models.FloatField(null=True)
    
  #Dividends
  avgAnnualDividend = models.FloatField(null=True)
  stdAnnualDividend = models.FloatField(null=True)
  estAnnualReturn = models.FloatField(null=True)
  
  #Returns
  currentAnnualROIC = models.FloatField(null=True)
  currentAnnualROA = models.FloatField(null=True)
  currentAnnualROE = models.FloatField(null=True)
  
  avgAnnualROIC = models.FloatField(null=True)
  avgAnnualROA = models.FloatField(null=True)
  avgAnnualROE = models.FloatField(null=True)
  
  currentQuarterROIC = models.FloatField(null=True)
  currentQuarterROA = models.FloatField(null=True)
  currentQuarterROE = models.FloatField(null=True)
  
  avgQuarterROIC = models.FloatField(null=True)
  avgQuarterROA = models.FloatField(null=True)
  avgQuarterROE = models.FloatField(null=True)
  
  currentAnnualPS = models.FloatField(null=True)
  avgAnnualPS = models.FloatField(null=True)
  enterpriseValue = models.FloatField(null=True)  
  EVtoEBITDA = models.FloatField(null=True)
  
  beta = models.FloatField(null=True)

  equityReturnRate = models.FloatField(null=True)
  DDMExpectedGrowthRate = models.FloatField(null=True)
  avgRetentionRate = models.FloatField(null=True)
  avgPayoutRate = models.FloatField(null=True)
  currentPayoutRate = models.FloatField(null=True)
  estimateDividend = models.FloatField(null=True)
  DDMPrice = models.FloatField(null=True)
  
  corporateTaxRate = models.FloatField(null=True)
  debtReturnRate = models.FloatField(null=True)
  
  WACC = models.FloatField(null=True)
  
  updateTime = models.DateField(auto_now_add=True)

  