from django.urls import path

from .views import FeedbackCreate, FeedbackListing, FeedbackThanks

app_name = 'feedback'

urlpatterns = [
    path('', FeedbackListing.as_view(), name='overview'),
    path('create/', FeedbackCreate.as_view(), name='create'),
    path('thanks/<int:pk>/', FeedbackThanks.as_view(), name='thanks'),
]
