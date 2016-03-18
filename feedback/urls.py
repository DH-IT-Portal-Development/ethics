from django.conf.urls import url

from .views import FeedbackCreate, FeedbackListing, FeedbackThanks

urlpatterns = [
    url(r'^$', FeedbackListing.as_view(), name='overview'),
    url(r'^create/$', FeedbackCreate.as_view(), name='create'),
    url(r'^thanks/(?P<pk>\d+)/$', FeedbackThanks.as_view(), name='thanks'),
]
