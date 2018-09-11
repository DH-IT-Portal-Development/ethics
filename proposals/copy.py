from django.utils import timezone

from studies.utils import copy_study_to_proposal
from .utils import generate_ref_number


def copy_proposal(self, form):
    from .models import Proposal

    # Save relationships
    parent = form.cleaned_data['parent']
    parent_pk = parent.pk
    relation = parent.relation
    applicants = parent.applicants.all()
    funding = parent.funding.all()
    copy_studies = parent.study_set.all()
    copy_wmo = None
    if hasattr(parent, 'wmo'):
        copy_wmo = parent.wmo

    # Create copy and save the this new model, set it to not-submitted
    copy_proposal = parent
    copy_proposal.pk = None
    copy_proposal.reference_number = generate_ref_number(self.request.user)
    copy_proposal.title = form.cleaned_data['title']
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

    return copy_proposal
