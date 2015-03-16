from django.conf.urls import url
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required

from .views import *

urlpatterns = [
    url(r'^$', HomeView.as_view(), name='home'),

    url(r'^applications/$', IndexView.as_view(), name='applications'),
    url(r'^concepts/$', ConceptsView.as_view(), name='concepts'),
    url(r'^archive/$', ArchiveView.as_view(), name='archive'),
    url(r'^(?P<pk>\d+)/$', DetailView.as_view(), name='detail'),

    url(r'^create/$', login_required(ProposalCreate.as_view())),
    url(r'^update/(?P<pk>\d+)/$', ProposalUpdate.as_view()),
    url(r'^delete/(?P<pk>\d+)/$', ProposalDelete.as_view()),
    
    url(r'^continue/(?P<pk>\d+)/$', WmoCreate.as_view()),
    url(r'^continue2/(?P<pk>\d+)/$', StudyCreate.as_view()),
    url(r'^continue3/(?P<pk>\d+)/$', TaskCreate.as_view()),

    url(r'^members/$', MembersView.as_view(), name='members'),
    url(r'^meetings/$', MeetingsView.as_view(), name='meetings'),
    url(r'^faq/$', FaqsView.as_view(), name='faq'),
]
