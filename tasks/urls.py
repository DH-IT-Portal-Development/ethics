from django.urls import path

from .views.session_views import TaskStart, TaskEnd, SessionDelete
from .views.task_views import TaskUpdate, TaskDelete

app_name = "tasks"

urlpatterns = [
    # Session(s)
    path("session/delete/<int:pk>/", SessionDelete.as_view(), name="session_delete"),
    path("start/<int:pk>/", TaskStart.as_view(), name="start"),
    path("end/<int:pk>/", TaskEnd.as_view(), name="end"),
    # Task(s)
    path("update/<int:pk>/", TaskUpdate.as_view(), name="update"),
    path("delete/<int:pk>/", TaskDelete.as_view(), name="delete"),
]
