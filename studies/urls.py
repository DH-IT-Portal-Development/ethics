from django.conf.urls import url

from .views.session_views import SessionStart, SessionEnd
from .views.study_views import StudyCreate, StudyUpdate, StudyDesign, StudyConsent, necessity_required

urlpatterns = [
    # Study
    url(r'^create/(?P<pk>\d+)/$', StudyCreate.as_view(), name='create'),
    url(r'^update/(?P<pk>\d+)/$', StudyUpdate.as_view(), name='update'),
    url(r'^design/(?P<pk>\d+)/$', StudyDesign.as_view(), name='design'),
    url(r'^consent/(?P<pk>\d+)/$', StudyConsent.as_view(), name='consent'),

    # Session(s)
    url(r'^session/start/(?P<pk>\d+)/$', SessionStart.as_view(), name='session_start'),
    url(r'^session/end/(?P<pk>\d+)/$', SessionEnd.as_view(), name='session_end'),

    # Checks on conditional fields
    url(r'^check_necessity_required/$', necessity_required, name='check_necessity_required'),
]
