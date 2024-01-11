from django.urls import path, include

from .views import \
    AllOpenProposalReviewsView, AllProposalReviewsView, DecisionListView, \
    InRevisionReviewsView, \
    DecisionMyOpenView, \
    ReviewClosedDecisionView, SupervisorDecisionOpenView, \
    DecisionOpenView, \
    ReviewDetailView, \
    ReviewAssignView, ReviewCloseView, ReviewDiscontinueView, \
    DecisionUpdateView, ToConcludeProposalView, ChangeChamberView, \
    CreateDecisionRedirectView, CommitteeMembersWorkloadView

app_name = 'reviews'

urlpatterns = [
    path('api/', include('reviews.api.urls', namespace='api')),
    path('<str:committee>/', DecisionListView.as_view(),
         name='my_archive'),
    path('<str:committee>/all/', AllProposalReviewsView.as_view(),
         name='archive'),
    path('<str:committee>/my_open/', DecisionMyOpenView.as_view(), name='my_open'),
    path('<str:committee>/open_decisions/', DecisionOpenView.as_view(),
         name='open'),
    path('<str:committee>/in_revision/',
         InRevisionReviewsView.as_view(),
         name='in_revision',
         ),
    path('<str:committee>/open/', AllOpenProposalReviewsView.as_view(), name='all_open'),
    path('<str:committee>/open_supervisors/', SupervisorDecisionOpenView.as_view(), name='open_supervisors'),
    path('<str:committee>/to_conclude/', ToConcludeProposalView.as_view(),
         name='to_conclude'),

    path('show/<int:pk>/', ReviewDetailView.as_view(), name='detail'),

    path('assign/<int:pk>/', ReviewAssignView.as_view(), name='assign'),
    path('<str:committee>/workload/', CommitteeMembersWorkloadView.as_view(), name='workload'),
    path('change_chamber/<int:pk>/', ChangeChamberView.as_view(),
         name='change_chamber'),
    path('close/<int:pk>/', ReviewCloseView.as_view(), name='close'),
    path('discontinue/<int:pk>/', ReviewDiscontinueView.as_view(), name='discontinue'),

    path('decide/<int:pk>/', DecisionUpdateView.as_view(), name='decide'),
    path('decide/closed/<int:pk>/', ReviewClosedDecisionView.as_view(), name='review-closed-decision'),
    path('decide/new/<int:review>/', CreateDecisionRedirectView.as_view(),
      name='decide_new'),
]
