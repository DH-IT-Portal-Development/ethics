from django.urls import path

from .views import ObservationCreate, ObservationUpdate, AttachmentsUpdate

app_name = "observations"

urlpatterns = [
    path("create/<int:pk>/", ObservationCreate.as_view(), name="create"),
    path("update/<int:pk>/", ObservationUpdate.as_view(), name="update"),
    path("attachments/<int:pk>/", AttachmentsUpdate.as_view(), name="attachments"),
]
