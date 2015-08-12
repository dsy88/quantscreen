from stock import models
from django.http.response import JsonResponse
from django.views.generic import View
from stock.models import YahooQuotes

class TopView(View):
  def get(self, request):
    ret = {}
    page = request.GET.get('page', 0)
    
    top = YahooQuotes.objects.order_by('-earningPerShare', \
                                       '-EPSEstimateCurrentYear')[:30]
    
    ret['top'] = [stock.to_json() for stock in top]   
    return JsonResponse(ret)
  
  