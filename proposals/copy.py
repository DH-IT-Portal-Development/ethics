from django.utils import timezone

from studies.utils import copy_study_to_proposal, copy_documents_to_proposal
from .utils import generate_ref_number, generate_revision_ref_number


def copy_proposal(original_proposal, is_revision, created_by_user):
    from .models import Proposal

    # Save relationships
    relation = original_proposal.relation
    applicants = original_proposal.applicants.all()
    funding = original_proposal.funding.all()

    # Create copy by retrieving a new object. This should ensure the original
    # object will not alter.
    copy_proposal = Proposal.objects.get(pk=original_proposal.pk)
    copy_proposal.pk = None

    copy_wmo = None
    if hasattr(original_proposal, 'wmo'):
        copy_wmo = original_proposal.wmo

    if is_revision:
        copy_proposal.reference_number = generate_revision_ref_number(
            original_proposal
        )
    else:
        copy_proposal.reference_number = generate_ref_number()

    copy_proposal.created_by = created_by_user
    copy_proposal.status = Proposal.DRAFT
    copy_proposal.status_review = None
    copy_proposal.pdf = None
    copy_proposal.date_created = timezone.now()
    copy_proposal.date_modified = timezone.now()
    copy_proposal.date_submitted_supervisor = None
    copy_proposal.date_reviewed_supervisor = None
    copy_proposal.date_submitted = None
    copy_proposal.date_reviewed = None
    copy_proposal.date_confirmed = None
    copy_proposal.is_exploration = False
    copy_proposal.in_course = False
    copy_proposal.is_revision = is_revision
    copy_proposal.has_minor_revision = False
    copy_proposal.minor_revision_description = None
    copy_proposal.save()

    # Copy references
    copy_proposal.relation = relation
    copy_proposal.applicants.set(applicants)
    copy_proposal.funding.set(funding)

    if is_revision:
        copy_proposal.parent = original_proposal
    else:
        copy_proposal.parent = None

    copy_proposal.save()

    # Copy linked models
    if copy_wmo:
        copy_wmo.pk = copy_proposal.pk
        copy_wmo.save()

    for study in original_proposal.study_set.all():
        copy_study_to_proposal(copy_proposal, study)

    if not copy_proposal.is_pre_approved:
        copy_documents_to_proposal(original_proposal.pk, copy_proposal)

    return copy_proposal
