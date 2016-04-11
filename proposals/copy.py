from django.utils import timezone

from studies.utils import copy_study_to_proposal
from .utils import generate_ref_number


def copy_proposal(self, form):
    parent = form.cleaned_data['parent']
    title = form.cleaned_data['title']

    # Save relationships
    relation = parent.relation
    applicants = parent.applicants.all()
    copy_studies = parent.study_set.all()
    copy_surveys = parent.survey_set.all()
    copy_wmo = None
    if hasattr(parent, 'wmo'):
        copy_wmo = parent.wmo

    # Create copy and save the this new model, set it to not-submitted
    copy_proposal = parent
    copy_proposal.pk = None
    copy_proposal.reference_number = generate_ref_number(self.request.user)
    copy_proposal.title = title
    copy_proposal.created_by = self.request.user
    copy_proposal.date_created = timezone.now()
    copy_proposal.date_modified = timezone.now()
    copy_proposal.date_submitted_supervisor = None
    copy_proposal.date_reviewed_supervisor = None
    copy_proposal.date_submitted = None
    copy_proposal.date_reviewed = None
    copy_proposal.save()

    # Copy references
    copy_proposal.relation = relation
    copy_proposal.applicants = applicants
    copy_proposal.parent = parent

    # Copy linked models
    if copy_wmo:
        copy_wmo.pk = copy_proposal.pk
        copy_wmo.save()

    for study in copy_studies:
        copy_study_to_proposal(copy_proposal, study)

    for survey in copy_surveys:
        copy_survey = survey
        copy_survey.pk = None
        copy_survey.proposal = copy_proposal
        copy_survey.save()
    copy_proposal.save()

    return copy_proposal
