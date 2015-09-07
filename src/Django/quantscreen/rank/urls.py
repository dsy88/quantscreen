from django.conf.urls import url, patterns
from rank.views import *
from django.views.decorators.csrf import csrf_exempt

urlpatterns = patterns('rank',
    url(r"^highgrowth$", csrf_exempt(HighGrowthView.as_view())),
    url(r"^highdividend$", csrf_exempt(HighDividendView.as_view())),
)