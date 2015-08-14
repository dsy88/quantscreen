from django.db import models
from stock.models import StockMeta
from django.db.models.lookups import StartsWith

class PEGRank(models.Model):
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
  
  assetQuarterGrowth = models.FloatField(null=True)
  assetAnnualGrowth = models.FloatField(null=True)
  
  PEGNextQuarter = models.FloatField(null=True)
  PEGNextAnnual = models.FloatField(null=True)
  
  QuarterTargetPrice = models.FloatField(null=True)
  AnnualTargePrice = models.FloatField(null=True)
  
  updateTime = models.DateField(auto_now_add=True)

  def to_json(self):
    data = {}
    data['symbol'] = self.stock.symbol
    
    for name in vars(self).keys():
      if name == 'stock' or name.startswith('_'):
        continue
      if name == "updateTime":
        data[name] = str(self.updateTime)
        continue
      data[name] = getattr(self, name)
    return data
  