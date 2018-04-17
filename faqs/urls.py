from django.conf.urls import url

from .views import FaqsView

app_name = 'faqs'

urlpatterns = [
    url(r'^$', FaqsView.as_view(), name='list'),
]
