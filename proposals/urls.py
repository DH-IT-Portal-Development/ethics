from django.conf.urls import url, include

from .views.proposal_views import ProposalsView, MyConceptsView, MySubmittedView, MyCompletedView, MyProposalsView, \
    ProposalCreate, ProposalUpdate, ProposalDelete, \
    ProposalStart, ProposalSubmit, ProposalSubmitted, \
    ProposalCopy, ProposalDifference, ProposalAsPdf, EmptyPDF, \
    ProposalCreatePreAssessment, ProposalUpdatePreAssessment, \
    ProposalStartPreAssessment, ProposalSubmitPreAssessment, ProposalSubmittedPreAssessment
from .views.study_views import StudyStart
from .views.wmo_views import WmoCreate, WmoUpdate, \
    WmoApplication, WmoCheck, check_wmo, \
    WmoCreatePreAssessment, WmoUpdatePreAssessment

urlpatterns = [
    # List views
    url(r'^archive/$', ProposalsView.as_view(), name='archive'),
    url(r'^my_concepts/$', MyConceptsView.as_view(), name='my_concepts'),
    url(r'^my_submitted/$', MySubmittedView.as_view(), name='my_submitted'),
    url(r'^my_completed/$', MyCompletedView.as_view(), name='my_completed'),
    url(r'^my_archive/$', MyProposalsView.as_view(), name='my_archive'),

    # Proposal
    url(r'^create/', include([
        url(r'^$', ProposalCreate.as_view(), name='create'),
        url(r'^pre/$', ProposalCreatePreAssessment.as_view(), name='create_pre'),
    ])),
    url(r'^update/(?P<pk>\d+)/', include([
        url(r'^$', ProposalUpdate.as_view(), name='update'),
        url(r'^pre/$', ProposalUpdatePreAssessment.as_view(), name='update_pre'),
    ])),
    url(r'^delete/(?P<pk>\d+)/$', ProposalDelete.as_view(), name='delete'),

    url(r'^start/', include([
        url(r'^$', ProposalStart.as_view(), name='start'),
        url(r'^pre/$', ProposalStartPreAssessment.as_view(), name='start_pre'),
    ])),
    url(r'^submit/(?P<pk>\d+)/', include([
        url(r'^$', ProposalSubmit.as_view(), name='submit'),
        url(r'^pre/$', ProposalSubmitPreAssessment.as_view(), name='submit_pre'),
    ])),
    url(r'^submitted/(?P<pk>\d+)/', include([
        url(r'^$', ProposalSubmitted.as_view(), name='submitted'),
        url(r'^pre/$', ProposalSubmittedPreAssessment.as_view(), name='submitted_pre'),
    ])),

    url(r'^study_start/(?P<pk>\d+)/$', StudyStart.as_view(), name='study_start'),

    url(r'^copy/$', ProposalCopy.as_view(), name='copy'),
    url(r'^diff/(?P<pk>\d+)/$', ProposalDifference.as_view(), name='diff'),

    url(r'^pdf/(?P<pk>\d+)/$', ProposalAsPdf.as_view(), name='pdf'),
    url(r'^pdf_empty/$', EmptyPDF.as_view(), name='empty_pdf'),

    # WMO
    url(r'^wmo/create/(?P<pk>\d+)/', include([
        url(r'^$', WmoCreate.as_view(), name='wmo_create'),
        url(r'^pre/$', WmoCreatePreAssessment.as_view(), name='wmo_create_pre'),
    ])),
    url(r'^wmo/update/(?P<pk>\d+)/', include([
        url(r'^$', WmoUpdate.as_view(), name='wmo_update'),
        url(r'^pre/$', WmoUpdatePreAssessment.as_view(), name='wmo_update_pre'),
    ])),
    url(r'^wmo/application/(?P<pk>\d+)/$', WmoApplication.as_view(), name='wmo_application'),
    url(r'^wmo/check/$', WmoCheck.as_view(), name='wmo_check'),
    url(r'^wmo/check_js/$', check_wmo, name='check_wmo'),
]
