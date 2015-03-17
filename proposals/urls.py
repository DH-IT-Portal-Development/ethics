from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from .views import *

urlpatterns = [
    # Home
    url(r'^$', HomeView.as_view(), name='home'),

    # Lists 
    url(r'^applications/$', IndexView.as_view(), name='applications'),
    url(r'^concepts/$', ConceptsView.as_view(), name='concepts'),
    url(r'^archive/$', ArchiveView.as_view(), name='archive'),
    url(r'^(?P<pk>\d+)/$', DetailView.as_view(), name='detail'),

    # Proposal
    url(r'^create/$', login_required(ProposalCreate.as_view())),
    url(r'^update/(?P<pk>\d+)/$', ProposalUpdate.as_view()),
    url(r'^delete/(?P<pk>\d+)/$', ProposalDelete.as_view()),
    
    # WMO
    url(r'^wmo/create/(?P<pk>\d+)/$', WmoCreate.as_view()),
    #url(r'^wmo/update/(?P<pk>\d+)/$', WmoUpdate.as_view()),

    # Study
    url(r'^study/create/(?P<pk>\d+)/$', StudyCreate.as_view()),
    #url(r'^study/update/(?P<pk>\d+)/$', StudyUpdate.as_view()),

    # Task(s)
    url(r'^task/create/(?P<pk>\d+)/$', TaskCreate.as_view()),
    #url(r'^task/update/(?P<pk>\d+)/$', TaskUpdate.as_view()),

    url(r'^members/$', MembersView.as_view(), name='members'),
    url(r'^meetings/$', MeetingsView.as_view(), name='meetings'),
    url(r'^faq/$', FaqsView.as_view(), name='faq'),
]
