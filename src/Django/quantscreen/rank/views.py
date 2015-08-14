from stock import models
from quantscreen.helper import json_response
from quantscreen.helper import BaseView
from django.utils.decorators import method_decorator
from stock.models import YahooQuotes, StockMeta
from rank.models import PEGRank
from datetime import datetime, timedelta

class TopView(BaseView):
  @method_decorator(json_response)
  def get(self, request):
    print request
    page = request.GET.get('page', 0)
    
    top = YahooQuotes.objects.order_by('-earningPerShare', \
                                       '-EPSEstimateCurrentYear')[:30]
    
    self.ret['top'] = [stock.to_json() for stock in top]   
    return self.ret
  

class PERankView(BaseView):
  @method_decorator(json_response)
  def get(self, request):
    page = request.GET.get('page', 0)
    
    dates = PEGRank.objects.dates('updateTime', 'day', order='DESC').distinct()
    
    for date in dates:
      top = PEGRank.objects.filter(updateTime=str(date), rate__isnull=False, rate__gt=0).order_by('rate')[:30]
      
      if len(top) > 0:
        break
      
    self.ret['top'] = [rank.to_json() for rank in top]
    return self.ret
  