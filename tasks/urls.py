from django.conf.urls import url

from .views.session_views import TaskStart, TaskEnd, SessionDelete
from .views.task_views import TaskUpdate, TaskDelete

urlpatterns = [
    # Session(s)
    url(r'^session/delete/(?P<pk>\d+)/$', SessionDelete.as_view(), name='session_delete'),
    url(r'^start/(?P<pk>\d+)/$', TaskStart.as_view(), name='start'),
    url(r'^end/(?P<pk>\d+)/$', TaskEnd.as_view(), name='end'),

    # Task(s)
    url(r'^update/(?P<pk>\d+)/$', TaskUpdate.as_view(), name='update'),
    url(r'^delete/(?P<pk>\d+)/$', TaskDelete.as_view(), name='delete'),
]
