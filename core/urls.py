from django.conf.urls import url

from .views import HomeView, check_requires, UserSearchView, UserDetailView, \
    DevSandboxView

app_name = 'core'

urlpatterns = [
    # Home
    url(r'^$', HomeView.as_view(), name='home'),

    # User detail page
    url(r'^user/(?P<pk>\d+)/', UserDetailView.as_view(), name='user_detail'),

    # User search
    url(r'^user_search/$', UserSearchView.as_view(), name='user_search'),

    # Checks on conditional fields
    url(r'^check_requires/$', check_requires, name='check_requires'),
    
    url(r'^dev/(?P<query>\w+)/$', DevSandboxView.as_view(), name='dev'),
    url(r'^dev/$', DevSandboxView.as_view(), name='dev')
]
