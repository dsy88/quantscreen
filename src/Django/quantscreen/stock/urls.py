from django.conf.urls import url, patterns
from stock.views import *
from django.views.decorators.csrf import csrf_exempt

urlpatterns = patterns('stock',
    url(r"^basic$", csrf_exempt(BasicInfoView.as_view())),
)