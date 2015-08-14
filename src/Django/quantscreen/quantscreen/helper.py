from django.http import HttpResponse, JsonResponse
from django.views.generic import View
from django.utils.decorators import method_decorator

import json

  
def json_response(method):
  def wrapper(*args, **kwargs):
    ret = method(*args, **kwargs)
    return JsonResponse(ret)
  
  return wrapper
  

class BaseView(View):
  ret = {}
  ret['status'] = 'OK'
  ret['status_code'] = 0
  