from django.conf.urls import url, patterns
from rank.views import *

urlpatterns = patterns(
    url(r"^top$", TopView.as_view()) 
)