from django.db import models
from stock.models import StockMeta
from django.db.models.lookups import StartsWith
from quantscreen.helper import JsonMethod

class PEGRank(models.Model, JsonMethod):
  stock = models.ForeignKey(StockMeta, 
                               related_name='PEGRank')
  rate = models.FloatField(null=True)
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
  
  updateTime = models.DateField(auto_now_add=True)
  
class DividendRank(models.Model, JsonMethod):
  stock = models.ForeignKey(StockMeta, related_name='DividendRank')
  
  avgAnnualDividend = models.FloatField(null=True)
  stdAnnualDividend = models.FloatField(null=True)
  estAnnualReturn = models.FloatField(null=True)
  
  rate = models.FloatField(null=True)
  updateTime = models.DateField(auto_now_add=True)

  
  