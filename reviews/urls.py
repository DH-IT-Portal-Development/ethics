from django.conf.urls import url

from .views import SupervisorView, CommissionView, DecisionListView, DecisionUpdateView

urlpatterns = [
    url(r'^decisions/$', DecisionListView.as_view(), name='home'),
    url(r'^as_supervisor/$', SupervisorView.as_view(), name='supervisor'),
    url(r'^as_commission/$', CommissionView.as_view(), name='commission'),
    url(r'^decide/(?P<pk>\d+)/$', DecisionUpdateView.as_view(), name='decide'),
]
