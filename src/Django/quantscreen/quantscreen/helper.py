from django.http import HttpResponse, JsonResponse
from django.views.generic import View
from django.utils.decorators import method_decorator
from django.db.models import Model
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


class JsonMethod(object):
  def to_json(self):
    data = {}
    for name in dir(self):
      if callable(name) or name.startswith("_"):
        continue
      
      val = getattr(self, name, None)
      if name in vars(self):  
        if isinstance(val, basestring):
          data[name] = val
        else:
          data[name] = str(val)
      if isinstance(val, Model):
        data[name] = val.to_json()
        
    return data  