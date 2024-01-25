from django.urls import path

from .views.session_views import SessionUpdate, SessionEnd, SessionDelete, SessionCreate
from .views.task_views import TaskUpdate, TaskDelete, TaskCreate

app_name = "tasks"

urlpatterns = [
    # Session(s)
    path("session/delete/<int:pk>/", SessionDelete.as_view(), name="session_delete"),
    path("session/create/<int:pk>/", SessionCreate.as_view(), name="session_create"),
    path("session/update/<int:pk>/", SessionUpdate.as_view(), name="session_update"),
    path("session/end/<int:pk>/", SessionEnd.as_view(), name="session_end"),
    # Task(s)
    path("update/<int:pk>/", TaskUpdate.as_view(), name="update"),
    path("create/<int:pk>", TaskCreate.as_view(), name="create"),
    path("delete/<int:pk>/", TaskDelete.as_view(), name="delete"),
]
