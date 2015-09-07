from stock import models
from quantscreen.helper import json_response
from quantscreen.helper import BaseView
from django.utils.decorators import method_decorator
from stock.models import YahooQuotes, StockMeta
from rank.models import Statistics
from datetime import datetime, timedelta

COUNT_PER_PAGE = 10

class HighGrowthView(BaseView):
  @method_decorator(json_response)
  def get(self, request):
    page = request.GET.get('page', 0)
    
    dates = Statistics.objects.dates('updateTime', 'day', order='DESC').distinct()
    
    for date in dates:
      q = Statistics.objects.filter(updateTime=str(date), \
                                 PEGNextQuarter__isnull=False, PEGNextQuarter__gt=0,\
                                 PEGNextAnnual__isnull=False, PEGNextAnnual__gt=0,\
                                 epsAnnualGrowth__gt=0.15,\
                                 epsQuarterGrowth__gt=0.05).\
                                  order_by('PEGNextAnnual', 'PEGNextQuarter')
      total = len(q) / COUNT_PER_PAGE
      top = q[:COUNT_PER_PAGE]
      if len(top) > 0:
        break
    
    self.ret['top'] = [stat.to_json() for stat in top]
    self.ret['page'] = page
    self.ret['total'] = total
    return self.ret
  
class HighDividendView(BaseView):
  @method_decorator(json_response)
  def get(self, request):
    page = request.GET.get('page', 0)
    
    dates = Statistics.objects.dates('updateTime', 'day', order='DESC').distinct()
    
    for date in dates:
      q = Statistics.objects.filter(updateTime=str(date), \
                                    estAnnualReturn__isnull=False, estAnnualReturn__gt=0).\
                                    order_by('-estAnnualReturn')
      total = len(q) / COUNT_PER_PAGE
      top = q[:COUNT_PER_PAGE]  
      if len(top) > 0:
        break
      
    self.ret['top'] = [stat.to_json() for stat in top]
    self.ret['page'] = page
    self.ret['total'] = total
    return self.ret