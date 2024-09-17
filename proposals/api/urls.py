from django.urls import path

from .views import (
    ProposalApiView,
    ProposalArchiveApiView,
)

app_name = "api"

urlpatterns = [
    path("archive/<str:committee>/", ProposalArchiveApiView.as_view(), name="archive"),
    path("user/", ProposalApiView.as_view(), name="my_proposals"),
]
