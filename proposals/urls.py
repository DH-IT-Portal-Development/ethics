from django.urls import path, include

from .views.proposal_views import CompareDocumentsView, MyConceptsView, \
    MyPracticeView, \
    MySubmittedView, MyCompletedView, MySupervisedView, MyProposalsView, \
    ProposalCreate, ProposalUpdate, ProposalDelete, ProposalStart, \
    ProposalDataManagement, ProposalSubmit, ProposalSubmitted, \
    ProposalConfirmation, ProposalCopy, ProposalCopyRevision, \
    ProposalDifference, ProposalAsPdf, ProposalCreatePreAssessment, \
    ProposalUpdatePreAssessment, ProposalStartPreAssessment, \
    ProposalSubmitPreAssessment, ProposalSubmittedPreAssessment, \
    ProposalCreatePractice, ProposalUpdatePractice, ProposalStartPractice, \
    ChangeArchiveStatusView, ProposalsExportView, ProposalStartPreApproved, \
    ProposalCreatePreApproved, ProposalSubmittedPreApproved, \
    ProposalSubmitPreApproved, ProposalUpdatePreApproved, \
    ProposalUsersOnlyArchiveView, \
    ProposalCopyAmendment, ProposalsPublicArchiveView, \
    ProposalUpdateDataManagement, TranslatedConsentFormsView

from .views.study_views import StudyStart, StudyConsent
from .views.wmo_views import WmoCreate, WmoUpdate, \
    WmoApplication, WmoCheck, check_wmo, \
    WmoCreatePreAssessment, WmoUpdatePreAssessment, WmoApplicationPreAssessment

app_name = 'proposals'

urlpatterns = [
    path('api/', include('proposals.api.urls', namespace='api')),
    # List views
    path('archive/', include([
        path('public/', ProposalsPublicArchiveView.as_view(),
             name='public_archive'),
        path('export/', ProposalsExportView.as_view(), name='archive_export'),
        path('export/<int:pk>/', ProposalsExportView.as_view(),
            name='archive_export'),
        path('archive_status/<int:pk>/', ChangeArchiveStatusView.as_view(),
            name='archive_status'),
        # WARNING! This one needs to be LAST in the list. (Django goes
        # through the list and picks the first one that fits, and the regex
        # will always fit for the other 2 URL's, effectively superseding them
        # if it's above them).
        path('<str:committee>/', ProposalUsersOnlyArchiveView.as_view(),
             name='archive'),
    ])),

    path('my_concepts/', MyConceptsView.as_view(), name='my_concepts'),
    path('my_practice/', MyPracticeView.as_view(), name='my_practice'),
    path('my_submitted/', MySubmittedView.as_view(), name='my_submitted'),
    path('my_completed/', MyCompletedView.as_view(), name='my_completed'),
    path('my_supervised/', MySupervisedView.as_view(), name='my_supervised'),
    path('my_archive/', MyProposalsView.as_view(), name='my_archive'),

    # Proposal
    path('create/', include([
        path('', ProposalCreate.as_view(), name='create'),
        path('pre/', ProposalCreatePreAssessment.as_view(),
             name='create_pre'),
        path('practice/<int:reason>/', ProposalCreatePractice.as_view(),
             name='create_practice'),
        path('pre_approved/', ProposalCreatePreApproved.as_view(),
             name='create_pre_approved'),
    ])),
    path('update/<int:pk>/', include([
        path('', ProposalUpdate.as_view(), name='update'),
        path('pre/', ProposalUpdatePreAssessment.as_view(),
             name='update_pre'),
        path('practice/', ProposalUpdatePractice.as_view(),
             name='update_practice'),
        path('pre_approved/', ProposalUpdatePreApproved.as_view(),
             name='update_pre_approved'),
    ])),
    path('delete/<int:pk>/', ProposalDelete.as_view(), name='delete'),

    path('start/', include([
        path('', ProposalStart.as_view(), name='start'),
        path('pre/', ProposalStartPreAssessment.as_view(), name='start_pre'),
        path('practice/', ProposalStartPractice.as_view(),
             name='start_practice'),
        path('pre_approved/', ProposalStartPreApproved.as_view(),
             name='start_pre_approved'),
    ])),

    path('data_management/<int:pk>/', ProposalDataManagement.as_view(),
         name='data_management'),
    path('update_data_management/<int:pk>/', ProposalUpdateDataManagement.as_view(), 
         name='update_data_management'),

    path('submit/<int:pk>/', include([
        path('', ProposalSubmit.as_view(), name='submit'),
        path('pre/', ProposalSubmitPreAssessment.as_view(),
             name='submit_pre'),
        path('pre_approved/', ProposalSubmitPreApproved.as_view(),
             name='submit_pre_approved'),
    ])),

    path('submitted/<int:pk>/', include([
        path('', ProposalSubmitted.as_view(), name='submitted'),
        path('pre/', ProposalSubmittedPreAssessment.as_view(),
             name='submitted_pre'),
        path('pre_approved/', ProposalSubmittedPreApproved.as_view(),
             name='submitted_pre_approved')
    ])),

    path('confirm/<int:pk>/', ProposalConfirmation.as_view(),
         name='confirmation'),

    path('study_start/<int:pk>/', StudyStart.as_view(),
         name='study_start'),

    path('consent/<int:pk>/', StudyConsent.as_view(), name='consent'),

    path('translated/<int:pk>/', TranslatedConsentFormsView.as_view(), name='translated'),

    path('copy/', include([
        path('', ProposalCopy.as_view(), name='copy'),
        path('revision/', ProposalCopyRevision.as_view(),
             name='copy_revision'),
        path('amendment/', ProposalCopyAmendment.as_view(),
             name='copy_amendment'),
    ])),
    path('diff/<int:pk>/', ProposalDifference.as_view(), name='diff'),

    path('pdf/<int:pk>/', ProposalAsPdf.as_view(), name='pdf'),

    # WMO
    path('wmo/create/<int:pk>/', include([
        path('', WmoCreate.as_view(), name='wmo_create'),
        path('pre/', WmoCreatePreAssessment.as_view(), name='wmo_create_pre'),
    ])),
    path('wmo/update/<int:pk>/', include([
        path('', WmoUpdate.as_view(), name='wmo_update'),
        path('pre/', WmoUpdatePreAssessment.as_view(), name='wmo_update_pre'),
    ])),
    path('wmo/application/<int:pk>/', include([
        path('', WmoApplication.as_view(), name='wmo_application'),
        path('pre/', WmoApplicationPreAssessment.as_view(), name='wmo_application_pre'),
    ])),
    path('wmo/check/', WmoCheck.as_view(), name='wmo_check'),
    path('wmo/check_js/', check_wmo, name='check_wmo'),

    path(
        'compare/', include([
            path(
                'consent/<int:old>/<int:new>/<str:attribute>/',
                CompareDocumentsView.as_view(),
                {
                    'type': 'documents'
                },
                name='compare_documents',
            ),
            path(
                'observation/<int:old>/<int:new>/approval_document/',
                CompareDocumentsView.as_view(),
                {
                    'type':      'observation',
                    'attribute': 'approval_document',
                },
                name='compare_observation_approval',
            ),
            path(
                'wmo/<int:old>/<int:new>/decision/',
                CompareDocumentsView.as_view(),
                {
                    'type':      'wmo',
                    'attribute': 'metc_decision_pdf',
                },
                name='compare_wmo_decision',
            ),
            path(
                'study/<int:old>/<int:new>/<str:attribute>/',
                CompareDocumentsView.as_view(),
                {
                    'type': 'proposal'
                },
                name='compare_proposal_docs',
            ),
        ])
    ),
]
