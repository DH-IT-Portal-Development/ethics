from django.conf.urls import url

from .views import \
    AllProposalReviewsView, DecisionListView, DecisionMyOpenView, \
    SupervisorDecisionOpenView, \
    DecisionOpenView, \
    ReviewDetailView, \
    ReviewAssignView, ReviewCloseView, \
    DecisionUpdateView, ToConcludeProposalView, ChangeChamberView, \
    CreateDecisionRedirectView

app_name = 'reviews'

urlpatterns = [
    url(r'^(?P<committee>\w+)/$', DecisionListView.as_view(),
        name='my_archive'),
    url(r'^(?P<committee>\w+)/all/$', AllProposalReviewsView.as_view(),
        name='archive'),
    url(r'^(?P<committee>\w+)/my_open/$', DecisionMyOpenView.as_view(), name='my_open'),
    url(r'^(?P<committee>\w+)/open/$', DecisionOpenView.as_view(), name='open'),
    url(r'^(?P<committee>\w+)/open_supervisors/$', SupervisorDecisionOpenView.as_view(), name='open_supervisors'),
    url(r'^(?P<committee>\w+)/to_conclude/$', ToConcludeProposalView.as_view(),
        name='to_conclude'),

    url(r'^show/(?P<pk>\d+)/$', ReviewDetailView.as_view(), name='detail'),

    url(r'^assign/(?P<pk>\d+)/$', ReviewAssignView.as_view(), name='assign'),
    url(r'^change_chamber/(?P<pk>\d+)/$', ChangeChamberView.as_view(),
        name='change_chamber'),
    url(r'^close/(?P<pk>\d+)/$', ReviewCloseView.as_view(), name='close'),

    url(r'^decide/(?P<pk>\d+)/$', DecisionUpdateView.as_view(), name='decide'),
    url(r'^decide/new/(?P<review>\d+)/$', CreateDecisionRedirectView.as_view(), name='decide_new')
]
