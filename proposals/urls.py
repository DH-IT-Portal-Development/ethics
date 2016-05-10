from django.conf.urls import url

from .views.proposal_views import ProposalsView, MyConceptsView, MySubmittedView, MyCompletedView, MyProposalsView, \
    ProposalCreate, ProposalUpdate, ProposalDelete, ProposalStart, ProposalSubmit, ProposalSubmitted, \
    ProposalCopy, ProposalAsPdf, EmptyPDF
from .views.study_views import StudyStart
from .views.wmo_views import WmoCreate, WmoUpdate, WmoApplication, WmoCheck, check_wmo

urlpatterns = [
    # List views
    url(r'^archive/$', ProposalsView.as_view(), name='archive'),
    url(r'^my_concepts/$', MyConceptsView.as_view(), name='my_concepts'),
    url(r'^my_submitted/$', MySubmittedView.as_view(), name='my_submitted'),
    url(r'^my_completed/$', MyCompletedView.as_view(), name='my_completed'),
    url(r'^my_archive/$', MyProposalsView.as_view(), name='my_archive'),

    # Proposal
    url(r'^create/$', ProposalCreate.as_view(), name='create'),
    url(r'^update/(?P<pk>\d+)/$', ProposalUpdate.as_view(), name='update'),
    url(r'^delete/(?P<pk>\d+)/$', ProposalDelete.as_view(), name='delete'),

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
    url(r'^wmo/application/(?P<pk>\d+)/$', WmoApplication.as_view(), name='wmo_application'),
    url(r'^wmo/check/$', WmoCheck.as_view(), name='wmo_check'),
    url(r'^wmo/check_js/$', check_wmo, name='check_wmo'),
]
