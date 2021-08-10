from django.urls import path

from .views import AllOpenReviewsApiView, MyDecisionsApiView, \
    MyOpenDecisionsApiView, OpenDecisionsApiView, \
    OpenSupervisorDecisionApiView, ToConcludeReviewApiView, AllReviewsApiView

app_name = 'api'

urlpatterns = [
    path('<str:committee>/decisions/',
         MyDecisionsApiView.as_view(),
         name='my_archive'),
    path('<str:committee>/my_open/',
         MyOpenDecisionsApiView.as_view(),
         name='my_open'),
    path('<str:committee>/open_decisions/',
         OpenDecisionsApiView.as_view(),
         name='open'),
    path('<str:committee>/open_supervisors/',
         OpenSupervisorDecisionApiView.as_view(),
         name='open_supervisors'),

    path('<str:committee>/open/',
         AllOpenReviewsApiView.as_view(),
         name='all_open'),
    path('<str:committee>/to_conclude/',
         ToConcludeReviewApiView.as_view(),
         name='to_conclude'),
    path('<str:committee>/archive/',
         AllReviewsApiView.as_view(),
         name='archive'),
]
