from django.urls import path

from .views import (
    ProposalArchiveApiView,
    MyConceptsApiView,
    MySubmittedApiView,
    MyCompletedApiView,
    MySupervisedApiView,
    MyPracticeApiView,
    MyProposalsApiView,
)

app_name = "api"

urlpatterns = [
    path("archive/<str:committee>/", ProposalArchiveApiView.as_view(), name="archive"),
    path("my_archive/", MyProposalsApiView.as_view(), name="my_archive"),
    path("my_concepts/", MyConceptsApiView.as_view(), name="my_concepts"),
    path("my_submitted/", MySubmittedApiView.as_view(), name="my_submitted"),
    path("my_completed/", MyCompletedApiView.as_view(), name="my_completed"),
    path("my_supervised/", MySupervisedApiView.as_view(), name="my_supervised"),
    path("my_practice/", MyPracticeApiView.as_view(), name="my_practice"),
]
