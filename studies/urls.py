from django.urls import path

from .views.study_views import (
    StudyUpdate,
    StudyPersonalData,
    StudyRegistration,
    StudyDesign,
    StudyUpdateAttachments,
    StudyEnd,
    has_adults,
    necessity_required,
)

app_name = "studies"

urlpatterns = [
    # Study
    path("update/<int:pk>/", StudyUpdate.as_view(), name="update"),
    path("personal_data/<int:pk>/", StudyPersonalData.as_view(), name="personal_data"),
    path("registration/<int:pk>/", StudyRegistration.as_view(), name="registration"),
    path("design/<int:pk>/", StudyDesign.as_view(), name="design"),
    path("end/<int:pk>/", StudyEnd.as_view(), name="design_end"),
    path("attachments/<int:pk>/", StudyUpdateAttachments.as_view(), name="attachments"),
    # Checks on conditional fields
    path("check_has_adults/", has_adults, name="check_has_adults"),
    path(
        "check_necessity_required/", necessity_required, name="check_necessity_required"
    ),
]
