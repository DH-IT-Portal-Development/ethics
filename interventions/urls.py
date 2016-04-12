from django.conf.urls import url

from .views import InterventionCreate, InterventionUpdate

urlpatterns = [
    url(r'^create/(?P<pk>\d+)/$', InterventionCreate.as_view(), name='create'),
    url(r'^update/(?P<pk>\d+)/$', InterventionUpdate.as_view(), name='update'),
]
