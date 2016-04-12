from django.conf.urls import url

from .views import HomeView, check_requires

urlpatterns = [
    # Home
    url(r'^$', HomeView.as_view(), name='home'),

    # Checks on conditional fields
    url(r'^check_requires/$', check_requires, name='check_requires'),
]
