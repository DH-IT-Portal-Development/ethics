from django.conf.urls import url

from .views import ObservationCreate, ObservationUpdate, AttachmentsUpdate

app_name = 'observations'

urlpatterns = [
    url(r'^create/(?P<pk>\d+)/$', ObservationCreate.as_view(), name='create'),
    url(r'^update/(?P<pk>\d+)/$', ObservationUpdate.as_view(), name='update'),
    url(r'^attachments/(?P<pk>\d+)/$', AttachmentsUpdate.as_view(), name='attachments')
]
