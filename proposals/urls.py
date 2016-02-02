from django.conf.urls import url

from .views.base_views import *
from .views.proposal_views import *
from .views.wmo_views import *
from .views.study_views import *
from .views.session_views import *
from .views.task_views import *

urlpatterns = [
    # Home
    url(r'^$', HomeView.as_view(), name='home'),

    # Lists
    url(r'^proposals-all/$', ProposalsView.as_view(), name='archive'),
    url(r'^concepts/$', MyConceptsView.as_view(), name='my_concepts'),
    url(r'^submitted/$', MySubmittedView.as_view(), name='my_submitted'),
    url(r'^completed/$', MyCompletedView.as_view(), name='my_completed'),
    url(r'^proposals/$', MyProposalsView.as_view(), name='my_archive'),

    # Proposal
    url(r'^create/$', ProposalCreate.as_view(), name='create'),
    url(r'^copy/$', ProposalCopy.as_view(), name='copy'),
    url(r'^update/(?P<pk>\d+)/$', ProposalUpdate.as_view(), name='update'),
    url(r'^delete/(?P<pk>\d+)/$', ProposalDelete.as_view(), name='delete'),
    url(r'^show/(?P<pk>\d+)/$', DetailView.as_view(), name='detail'),
    url(r'^pdf/(?P<pk>\d+)/$', ProposalAsPdf.as_view(), name='pdf'),

    url(r'^consent/(?P<pk>\d+)/$', ProposalUploadConsent.as_view(), name='consent'),
    url(r'^submit/(?P<pk>\d+)/$', ProposalSubmit.as_view(), name='submit'),

    # WMO
    url(r'^wmo/create/(?P<pk>\d+)/$', WmoCreate.as_view(), name='wmo_create'),
    url(r'^wmo/update/(?P<pk>\d+)/$', WmoUpdate.as_view(), name='wmo_update'),
    url(r'^wmo/check/$', WmoCheck.as_view(), name='wmo_check'),
    url(r'^wmo/check_js/$', check_wmo, name='check_wmo'),

    # Study
    url(r'^study/create/(?P<pk>\d+)/$', StudyCreate.as_view(), name='study_create'),
    url(r'^study/update/(?P<pk>\d+)/$', StudyUpdate.as_view(), name='study_update'),

    # Session(s)
    url(r'^session_start/(?P<pk>\d+)/$', ProposalSessionStart.as_view(), name='session_start'),
    url(r'^session_end/(?P<pk>\d+)/$', ProposalSessionEnd.as_view(), name='session_end'),
    url(r'^session_add/(?P<pk>\d+)/$', add_session, name='session_add'),

    url(r'^session/delete/(?P<pk>\d+)/$', SessionDelete.as_view(), name='session_delete'),
    url(r'^task_start/(?P<pk>\d+)/$', TaskStart.as_view(), name='task_start'),
    url(r'^task_end/(?P<pk>\d+)/$', TaskEnd.as_view(), name='task_end'),
    url(r'^task_add/(?P<pk>\d+)/$', add_task, name='task_add'),

    # Task(s)
    url(r'^task/update/(?P<pk>\d+)/$', TaskUpdate.as_view(), name='task_update'),
    url(r'^task/delete/(?P<pk>\d+)/$', TaskDelete.as_view(), name='task_delete'),

    url(r'^faq/$', FaqsView.as_view(), name='faq'),

    url(r'^check_requires/$', check_requires, name='check_requires'),
]
