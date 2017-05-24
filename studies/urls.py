from django.conf.urls import url

from .views.session_views import SessionStart
from .views.study_views import StudyUpdate, StudyDesign, StudyConsent, StudyUpdateAttachments, StudyEnd, \
    has_adults, necessity_required

urlpatterns = [
    # Study
    url(r'^update/(?P<pk>\d+)/$', StudyUpdate.as_view(), name='update'),

    url(r'^design/(?P<pk>\d+)/$', StudyDesign.as_view(), name='design'),
    url(r'^end/(?P<pk>\d+)/$', StudyEnd.as_view(), name='design_end'),

    url(r'^consent/(?P<pk>\d+)/$', StudyConsent.as_view(), name='consent'),

    url(r'^attachments/(?P<pk>\d+)/$', StudyUpdateAttachments.as_view(), name='attachments'),

    # Session(s)
    url(r'^session/start/(?P<pk>\d+)/$', SessionStart.as_view(), name='session_start'),

    # Checks on conditional fields
    url(r'^check_has_adults/$', has_adults, name='check_has_adults'),
    url(r'^check_necessity_required/$', necessity_required, name='check_necessity_required'),
]
