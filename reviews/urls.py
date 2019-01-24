from django.conf.urls import url

from .views import \
    DecisionListView, DecisionMyOpenView, SupervisorDecisionOpenView, DecisionOpenView, \
    ReviewDetailView, \
    ReviewAssignView, ReviewCloseView, \
    DecisionUpdateView, ToConcludeProposalView

app_name = 'reviews'

urlpatterns = [
    url(r'^$', DecisionListView.as_view(), name='my_archive'),
    url(r'^my_open/$', DecisionMyOpenView.as_view(), name='my_open'),
    url(r'^open/$', DecisionOpenView.as_view(), name='open'),
    url(r'^open_supervisors/$', SupervisorDecisionOpenView.as_view(), name='open_supervisors'),
    url(r'^to_conclude/$', ToConcludeProposalView.as_view(),
        name='to_conclude'),

    url(r'^show/(?P<pk>\d+)/$', ReviewDetailView.as_view(), name='detail'),

    url(r'^assign/(?P<pk>\d+)/$', ReviewAssignView.as_view(), name='assign'),
    url(r'^close/(?P<pk>\d+)/$', ReviewCloseView.as_view(), name='close'),

    url(r'^decide/(?P<pk>\d+)/$', DecisionUpdateView.as_view(), name='decide'),
]
