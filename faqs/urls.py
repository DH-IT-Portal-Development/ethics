from django.conf.urls import url

from .views import FaqsView

urlpatterns = [
    url(r'^$', FaqsView.as_view(), name='list'),
]
