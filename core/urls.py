from django.conf.urls import url

from .views import HomeView, check_requires, UserSearchView

app_name = 'core'

urlpatterns = [
    # Home
    url(r'^$', HomeView.as_view(), name='home'),

    # User search
    url(r'^user_search/$', UserSearchView.as_view(), name='user_search'),

    # Checks on conditional fields
    url(r'^check_requires/$', check_requires, name='check_requires'),
]
