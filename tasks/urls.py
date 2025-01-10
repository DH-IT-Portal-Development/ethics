from django.urls import path

from .views.session_views import (
    SessionUpdate,
    SessionEnd,
    SessionDelete,
    SessionCreate,
    SessionStart,
    SessionOverview,
)
from .views.task_views import TaskUpdate, TaskDelete, TaskCreate

app_name = "tasks"

urlpatterns = [
    # Session(s)
    path("session/start/<int:pk>/", SessionStart.as_view(), name="session_start"),
    path("session/delete/<int:pk>/", SessionDelete.as_view(), name="session_delete"),
    path("session/create/<int:pk>/", SessionCreate.as_view(), name="session_create"),
    path("session/update/<int:pk>/", SessionUpdate.as_view(), name="session_update"),
    path("session/end/<int:pk>/", SessionEnd.as_view(), name="session_end"),
    path(
        "session/overview/<int:pk>/", SessionOverview.as_view(), name="session_overview"
    ),
    # Task(s)
    path("update/<int:pk>/", TaskUpdate.as_view(), name="update"),
    path("create/<int:pk>", TaskCreate.as_view(), name="create"),
    path("delete/<int:pk>/", TaskDelete.as_view(), name="delete"),
]
