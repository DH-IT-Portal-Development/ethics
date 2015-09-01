from django.conf.urls import url

from .views import *

urlpatterns = [
    # Home
    url(r'^$', HomeView.as_view(), name='home'),

    # Lists
    url(r'^archive/$', ArchiveView.as_view(), name='archive'),
    url(r'^applications/$', IndexView.as_view(), name='my_archive'),
    url(r'^concepts/$', ConceptsView.as_view(), name='my_concepts'),

    # Proposal
    url(r'^create/$', ProposalCreate.as_view(), name='create'),
    url(r'^copy/$', ProposalCopy.as_view(), name='copy'),
    url(r'^update/(?P<pk>\d+)/$', ProposalUpdate.as_view(), name='update'),
    url(r'^delete/(?P<pk>\d+)/$', ProposalDelete.as_view(), name='delete'),
    url(r'^(?P<pk>\d+)/$', DetailView.as_view(), name='detail'),

    url(r'^consent/(?P<pk>\d+)/$', ProposalUploadConsent.as_view(), name='consent'),
    url(r'^submit/(?P<pk>\d+)/$', ProposalSubmit.as_view(), name='submit'),

    # WMO
    url(r'^wmo/create/(?P<pk>\d+)/$', WmoCreate.as_view(), name='wmo_create'),
    url(r'^wmo/update/(?P<pk>\d+)/$', WmoUpdate.as_view(), name='wmo_update'),

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
    url(r'^task/create/(?P<pk>\d+)/$', TaskCreate.as_view(), name='task_create'),
    url(r'^task/update/(?P<pk>\d+)/$', TaskUpdate.as_view(), name='task_update'),
    url(r'^task/delete/(?P<pk>\d+)/$', TaskDelete.as_view(), name='task_delete'),

    url(r'^members/$', MembersView.as_view(), name='members'),
    url(r'^meetings/$', MeetingsView.as_view(), name='meetings'),
    url(r'^faq/$', FaqsView.as_view(), name='faq'),

    url(r'^requires_supervisor/$', requires_supervisor, name='requires_supervisor'),
]
