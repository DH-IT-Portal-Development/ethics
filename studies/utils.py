from __future__ import division

from interventions.utils import copy_intervention_to_study
from observations.utils import copy_observation_to_study
from tasks.utils import copy_session_to_study

STUDY_PROGRESS_START = 10
STUDY_PROGRESS_TOTAL = 90


def check_has_adults(selected_age_groups):
    """
    Checks whether the given AgeGroups include adults.
    """
    from .models import AgeGroup

    adult_age_groups = AgeGroup.objects.filter(is_adult=True).values_list(
        "id", flat=True
    )
    return bool(set(selected_age_groups).intersection(adult_age_groups))


def check_necessity_required(proposal, age_groups, legally_incapable):
    """
    This call checks whether the necessity questions are required. They are required when:
    - The researcher requires a supervisor AND one of these cases applies:
    * A selected AgeGroup requires details.
    * Participants are legally incapable.
    """
    from .models import AgeGroup

    if proposal.relation and not proposal.relation.needs_supervisor:
        result = False
    else:
        required_values = AgeGroup.objects.filter(needs_details=True).values_list(
            "id", flat=True
        )
        result = bool(set(required_values).intersection(age_groups))
        result |= bool(legally_incapable)
    return result


def get_study_progress(study, is_end=False):
    if not study:
        return STUDY_PROGRESS_START
    progress = STUDY_PROGRESS_TOTAL / study.proposal.studies_number
    if not is_end:
        progress *= study.order - 1
    else:
        progress *= study.order
    return int(STUDY_PROGRESS_START + progress)


def create_documents_for_study(study):
    from .models import Documents

    d = Documents()
    d.proposal = study.proposal
    d.study = study
    d.save()


def copy_study_to_proposal(proposal, original_study):
    """
    Copies the given Study to the given Proposal.
    :param proposal: the current Proposal
    :param study: the current Study
    :return: the Proposal appended with the details of the given Study.
    """
    from studies.models import Study

    age_groups = original_study.age_groups.all()
    traits = original_study.traits.all()
    compensation = original_study.compensation
    recruitment = original_study.recruitment.all()
    special_details = original_study.special_details.all()
    intervention = original_study.get_intervention()
    observation = original_study.get_observation()
    sessions = original_study.get_sessions()
    registrations = original_study.registrations.all()
    registration_kinds = original_study.registration_kinds.all()

    s = Study.objects.get(pk=original_study.pk)
    s.pk = None
    s.proposal = proposal
    s.save()

    s.age_groups.set(age_groups)
    s.traits.set(traits)
    s.compensation = compensation
    s.recruitment.set(recruitment)
    s.special_details.set(special_details)
    s.registrations.set(registrations)
    s.registration_kinds.set(registration_kinds)

    s.save()

    if intervention:
        copy_intervention_to_study(s, intervention)
    if observation:
        copy_observation_to_study(s, observation)
    for session in sessions:
        copy_session_to_study(s, session)

    copy_documents_to_study(original_study.pk, s)


def copy_documents_to_study(study_old, study):
    from .models import Documents

    try:
        # Study will automatically create an empty Documents entry for itself on
        # save. We don't want that one, so we delete that one before copying the
        # old one over.
        empty_documents = Documents.objects.get(study=study)
        if empty_documents:
            empty_documents.delete()
    except Documents.DoesNotExist:
        pass

    documents = Documents.objects.get(study__pk=study_old)

    d = documents
    d.pk = None
    d.proposal = study.proposal
    d.study = study
    d.save()


def copy_documents_to_proposal(proposal_old, proposal):
    from .models import Documents

    for documents in Documents.objects.filter(proposal__pk=proposal_old, study=None):
        d = documents
        d.pk = None
        d.proposal = proposal
        d.save()
