from django.conf.urls import url

from .views.proposal_views import ProposalsView, MyConceptsView, MySubmittedView, MyCompletedView, MyProposalsView, \
    ProposalCreate, ProposalUpdate, ProposalDelete, ProposalStart, ProposalSubmit, ProposalSubmitted, \
    DetailView, ProposalCopy, ProposalAsPdf, EmptyPDF
from .views.study_views import StudyStart
from .views.wmo_views import WmoCreate, WmoUpdate, WmoCheck, check_wmo

urlpatterns = [
    # List views
    url(r'^archive/$', ProposalsView.as_view(), name='archive'),
    url(r'^concepts/$', MyConceptsView.as_view(), name='my_concepts'),
    url(r'^submitted/$', MySubmittedView.as_view(), name='my_submitted'),
    url(r'^completed/$', MyCompletedView.as_view(), name='my_completed'),
    url(r'^proposals/$', MyProposalsView.as_view(), name='my_archive'),

    # Proposal
    url(r'^create/$', ProposalCreate.as_view(), name='create'),
    url(r'^update/(?P<pk>\d+)/$', ProposalUpdate.as_view(), name='update'),
    url(r'^delete/(?P<pk>\d+)/$', ProposalDelete.as_view(), name='delete'),
    url(r'^show/(?P<pk>\d+)/$', DetailView.as_view(), name='detail'),

    url(r'^start/$', ProposalStart.as_view(), name='start'),
    url(r'^study_start/(?P<pk>\d+)/$', StudyStart.as_view(), name='study_start'),
    url(r'^submit/(?P<pk>\d+)/$', ProposalSubmit.as_view(), name='submit'),
    url(r'^submitted/$', ProposalSubmitted.as_view(), name='submitted'),

    url(r'^copy/$', ProposalCopy.as_view(), name='copy'),

    url(r'^pdf/(?P<pk>\d+)/$', ProposalAsPdf.as_view(), name='pdf'),
    url(r'^pdf_empty/$', EmptyPDF.as_view(), name='empty_pdf'),

    # WMO
    url(r'^wmo/create/(?P<pk>\d+)/$', WmoCreate.as_view(), name='wmo_create'),
    url(r'^wmo/update/(?P<pk>\d+)/$', WmoUpdate.as_view(), name='wmo_update'),
    url(r'^wmo/check/$', WmoCheck.as_view(), name='wmo_check'),
    url(r'^wmo/check_js/$', check_wmo, name='check_wmo'),
]
