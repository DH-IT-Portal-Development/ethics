from django.urls import path

from .views import FaqsView

app_name = 'faqs'

urlpatterns = [
    path('', FaqsView.as_view(), name='list'),
]
