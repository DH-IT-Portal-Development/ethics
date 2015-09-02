from django.conf.urls import url

from .views import FeedbackCreate, FeedbackListing

urlpatterns = [
    url(r'^$', FeedbackListing.as_view(), name='overview'),
    url(r'^create/$', FeedbackCreate.as_view(), name='create'),
]
