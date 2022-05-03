from django.utils import timezone

from studies.utils import copy_study_to_proposal, copy_documents_to_proposal
from .utils import generate_ref_number, generate_revision_ref_number


def copy_proposal(self, form):
    from .models import Proposal

    # Save relationships
    parent = form.cleaned_data['parent']
    parent_pk = parent.pk
    relation = parent.relation
    # We convert to list to force evaluation of the QS. Otherwise,
    # the evaluation will happen after we've updated the proposal's ID and
    # the queryset will try to retrieve the new (non-existing) data instead
    # of the old
    applicants = list(parent.applicants.all())
    funding = list(parent.funding.all())
    copy_studies = list(parent.study_set.all())
    copy_wmo = None
    if hasattr(parent, 'wmo'):
        copy_wmo = parent.wmo

    # Create copy and save the this new model, set it to not-submitted
    copy_proposal = parent
    copy_proposal.pk = None

    if form.cleaned_data['is_revision']:
        copy_proposal.reference_number = generate_revision_ref_number(parent)
    else:
        copy_proposal.reference_number = generate_ref_number()

    copy_proposal.created_by = self.request.user
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
    copy_proposal.is_revision = form.cleaned_data['is_revision']
    copy_proposal.save()

    # Copy references
    copy_proposal.relation = relation
    copy_proposal.applicants.set(applicants)
    copy_proposal.funding.set(funding)
    copy_proposal.parent = Proposal.objects.get(pk=parent_pk)
    copy_proposal.save()

    # Copy linked models
    if copy_wmo:
        copy_wmo.pk = copy_proposal.pk
        copy_wmo.save()

    for study in copy_studies:
        copy_study_to_proposal(copy_proposal, study)

    if not copy_proposal.is_pre_approved:
        copy_documents_to_proposal(parent_pk, copy_proposal)

    return copy_proposal
