from django.conf.urls import url

from .views import SupervisorView, CommissionView, DecisionListView, ReviewDetailView, ReviewAssignView, ReviewCloseView, DecisionUpdateView

urlpatterns = [
    url(r'^decisions/$', DecisionListView.as_view(), name='home'),
    url(r'^as_supervisor/$', SupervisorView.as_view(), name='supervisor'),
    url(r'^as_commission/$', CommissionView.as_view(), name='commission'),

    url(r'^show/(?P<pk>\d+)/$', ReviewDetailView.as_view(), name='detail'),

    url(r'^assign/(?P<pk>\d+)/$', ReviewAssignView.as_view(), name='assign'),
    url(r'^close/(?P<pk>\d+)/$', ReviewCloseView.as_view(), name='close'),

    url(r'^decide/(?P<pk>\d+)/$', DecisionUpdateView.as_view(), name='decide'),
]
