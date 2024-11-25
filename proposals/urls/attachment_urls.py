from django.urls import path, include

from proposals.models import Proposal
from studies.models import Study

from proposals.views.attachment_views import (
    ProposalAttachView,
    ProposalDetachView,
    ProposalAttachmentsView,
    ProposalUpdateAttachmentView,
    ProposalAttachmentDownloadView,
)

from proposals.views.proposal_views import (
    CompareAttachmentsView,
)

attachment_urls = [
    path(
        "attachments/<int:pk>/",
        ProposalAttachmentsView.as_view(),
        name="attachments",
    ),
    path(
        "attach_proposal/<str:kind>/<int:other_pk>/",
        ProposalAttachView.as_view(
            owner_model=Proposal,
            editing=False,
        ),
        name="attach_proposal",
    ),
    path(
        "attach_study/<str:kind>/<int:other_pk>/",
        ProposalAttachView.as_view(
            owner_model=Study,
            editing=False,
        ),
        name="attach_study",
    ),
    path(
        "attach_proposal/<int:other_pk>/",
        ProposalAttachView.as_view(
            owner_model=Proposal,
            editing=False,
        ),
        name="attach_proposal",
    ),
    path(
        "attach_study/<int:other_pk>/",
        ProposalAttachView.as_view(owner_model=Study, editing=False),
        name="attach_study",
    ),
    path(
        "<int:proposal_pk>/detach/<int:attachment_pk>/",
        ProposalDetachView.as_view(),
        name="detach_file",
    ),
    path(
        "attachments/<int:other_pk>/edit/<int:attachment_pk>/",
        ProposalUpdateAttachmentView.as_view(
            editing=True,
        ),
        name="update_attachment",
    ),
    path(
        "attachments/<int:proposal_pk>/download/<int:attachment_pk>/",
        ProposalAttachmentDownloadView.as_view(),
        name="download_attachment",
    ),
    path(
        "attachments/<int:proposal_pk>/download_original/<int:attachment_pk>/",
        ProposalAttachmentDownloadView.as_view(
            original_filename=True,
        ),
        name="download_attachment_original",
    ),
    path(
        "compare/<int:proposal_pk>/<int:old_pk>/<int:new_pk>/",
        CompareAttachmentsView.as_view(),
        name="compare_attachments",
    ),
]
