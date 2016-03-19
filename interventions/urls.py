from django.conf.urls import url

from .views import InterventionCreate, InterventionUpdate

urlpatterns = [
    url(r'^intervention/create/(?P<pk>\d+)/$', InterventionCreate.as_view(), name='create'),
    url(r'^intervention/update/(?P<pk>\d+)/$', InterventionUpdate.as_view(), name='update'),
]