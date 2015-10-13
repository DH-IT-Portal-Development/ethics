from django.conf.urls import url

from .views import *

urlpatterns = [
    url(r'^as_supervisor/$', SupervisorView.as_view(), name='supervisor'),
    url(r'^as_commission/$', CommissionView.as_view(), name='commission'),
    url(r'^decide/(?P<pk>\d+)/$', DecisionView.as_view(), name='decide'),
]
