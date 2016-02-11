from django.conf.urls import url

from .views import FeedbackCreate, FeedbackListing, FaqsView

urlpatterns = [
    url(r'^$', FeedbackListing.as_view(), name='overview'),
    url(r'^create/$', FeedbackCreate.as_view(), name='create'),

    url(r'^faq/$', FaqsView.as_view(), name='faq'),
]
