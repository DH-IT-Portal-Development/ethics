from django.conf.urls import url

from .views import ObservationCreate, ObservationUpdate

urlpatterns = [
    url(r'^observation/create/(?P<pk>\d+)/$', ObservationCreate.as_view(), name='create'),
    url(r'^observation/update/(?P<pk>\d+)/$', ObservationUpdate.as_view(), name='update'),
]