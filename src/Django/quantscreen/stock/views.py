from django.shortcuts import render
import json

from quantscreen.helper import json_response
from quantscreen.helper import BaseView
from django.utils.decorators import method_decorator
from stock.models import StockMeta, YahooQuotes

# Create your views here.
class BasicInfoView(BaseView):
  @method_decorator(json_response)
  def get(self, request):
    symbol = request.GET.get('symbol', 0)
    
    if symbol:
      stock = StockMeta.objects.filter(symbol=symbol).order_by('updateTime')[:1]
      if stock: 
        self.ret['meta'] = stock[0].to_json()
      
      yahoo = YahooQuotes.objects.filter(symbol=symbol).order_by('updateTime')[:1]
      if yahoo:
        self.ret['yahoo'] = yahoo[0].to_json()
    
    return self.ret