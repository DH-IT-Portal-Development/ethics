from django.conf.urls import url

from .views import \
    DecisionOpenListView, DecisionListView,\
    ReviewDetailView, \
    ReviewAssignView, ReviewCloseView, \
    DecisionUpdateView

urlpatterns = [
    url(r'^$', DecisionListView.as_view(), name='home'),
    url(r'^open/$', DecisionOpenListView.as_view(), name='open'),

    url(r'^show/(?P<pk>\d+)/$', ReviewDetailView.as_view(), name='detail'),

    url(r'^assign/(?P<pk>\d+)/$', ReviewAssignView.as_view(), name='assign'),
    url(r'^close/(?P<pk>\d+)/$', ReviewCloseView.as_view(), name='close'),

    url(r'^decide/(?P<pk>\d+)/$', DecisionUpdateView.as_view(), name='decide'),
]
