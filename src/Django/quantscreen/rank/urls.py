from django.conf.urls import url, patterns
from rank.views import *
from django.views.decorators.csrf import csrf_exempt

urlpatterns = patterns('rank',
    url(r"^top$", csrf_exempt(TopView.as_view())),
    url(r"^pegtop$", csrf_exempt(PERankView.as_view())),
    url(r"^dividendtop$", csrf_exempt(DividendView.as_view())),
)