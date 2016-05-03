from django.conf.urls import url

from .views.session_views import SessionStart
from .views.study_views import StudyUpdate, StudyDesign, StudyConsent, StudyEnd, necessity_required
from .views.survey_views import StudySurvey

urlpatterns = [
    # Study
    url(r'^update/(?P<pk>\d+)/$', StudyUpdate.as_view(), name='update'),
    url(r'^design/(?P<pk>\d+)/$', StudyDesign.as_view(), name='design'),
    url(r'^consent/(?P<pk>\d+)/$', StudyConsent.as_view(), name='consent'),
    url(r'^end/(?P<pk>\d+)/$', StudyEnd.as_view(), name='session_end'),

    # Session(s)
    url(r'^session/start/(?P<pk>\d+)/$', SessionStart.as_view(), name='session_start'),

    # Survey(s)
    url(r'^survey/(?P<pk>\d+)/$', StudySurvey.as_view(), name='survey'),

    # Checks on conditional fields
    url(r'^check_necessity_required/$', necessity_required, name='check_necessity_required'),
]
