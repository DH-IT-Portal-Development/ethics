from django.conf.urls import url
from django.views.generic import TemplateView

from .views import *

urlpatterns = [
    url(r'^$', HomeView.as_view(), name='index'),

    url(r'^applications/$', IndexView.as_view(), name='applications'),
    url(r'^concepts/$', ConceptsView.as_view(), name='concepts'),
    url(r'^archive/$', ArchiveView.as_view(), name='archive'),
    url(r'^(?P<pk>\d+)/$', DetailView.as_view(), name='detail'),

    #url(r'^add_proposal/$', views.add_proposal, name='add_proposal'),
    #, forms.ApplicationForm2, forms.ApplicationForm3, forms.ApplicationForm4
    #url(r'^create/$', views.ApplicationWizard.as_view([forms.ApplicationForm1])),

    url(r'^create/$', ProposalCreate.as_view()),
    url(r'^update/(?P<pk>\d+)/$', ProposalUpdate.as_view()),
    url(r'^delete/(?P<pk>\d+)/$', ProposalDelete.as_view()),
    
    url(r'^continue/(?P<pk>\d+)/$', WmoCreate.as_view()),
    url(r'^continue2/(?P<pk>\d+)/$', StudyCreate.as_view()),

    url(r'^faq/$', TemplateView.as_view(template_name='proposals/faq.html'), name='faq'),
]
