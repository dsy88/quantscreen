from stock import models
from quantscreen.helper import json_response
from quantscreen.helper import BaseView
from django.utils.decorators import method_decorator
from stock.models import YahooQuotes, StockMeta
from rank.models import PEGRank, DividendRank
from datetime import datetime, timedelta

class TopView(BaseView):
  @method_decorator(json_response)
  def get(self, request):
    print request
    page = request.GET.get('page', 0)
    
    q = YahooQuotes.objects.order_by('-earningPerShare', \
                                       '-EPSEstimateCurrentYear')[:30]
    total = len(q)
    top = q[:30]
    
    self.ret['top'] = [stock.to_json() for stock in top]
    self.ret['page'] = page
    self.ret['total'] = total   
    return self.ret
  

class PERankView(BaseView):
  @method_decorator(json_response)
  def get(self, request):
    page = request.GET.get('page', 0)
    
    dates = PEGRank.objects.dates('updateTime', 'day', order='DESC').distinct()
    
    for date in dates:
      q = PEGRank.objects.filter(updateTime=str(date), \
                                   rate__isnull=False, rate__gt=0).\
                            order_by('rate')
      total = len(q)
      top = q[:30]
      if len(top) > 0:
        break
    
    self.ret['top'] = [rank.to_json() for rank in top]
    self.ret['page'] = page
    self.ret['total'] = total
    return self.ret
  
class DividendView(BaseView):
  @method_decorator(json_response)
  def get(self, request):
    page = request.GET.get('page', 0)
    
    dates = PEGRank.objects.dates('updateTime', 'day', order='DESC').distinct()
    
    for date in dates:
      q = DividendRank.objects.filter(updateTime=str(date), \
                                   rate__isnull=False, rate__gt=0).\
                            unique().order_by('rate')[:30]
      total = len(q)
      top = q[:30]
      
      if len(top) > 0:
        break
      
    self.ret['top'] = [rank.to_json() for rank in top]
    self.ret['page'] = page
    self.ret['total'] = total
    return self.ret