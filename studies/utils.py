from __future__ import division

from interventions.utils import copy_intervention_to_study
from observations.utils import copy_observation_to_study
from tasks.utils import copy_session_to_study
from .models import AgeGroup

STUDY_PROGRESS_START = 10
STUDY_PROGRESS_TOTAL = 90


def check_necessity_required(proposal, age_groups, has_traits, legally_incapable):
    """
    This call checks whether the necessity questions are required. They are required when:
    - The researcher requires a supervisor AND one of these cases applies:
        - A selected AgeGroup requires details.
        - Participants have been selected on certain traits.
        - Participants are legally incapable.
    """
    if not proposal.relation.needs_supervisor:
        result = False
    else:
        required_values = AgeGroup.objects.filter(needs_details=True).values_list('id', flat=True)
        result = bool(set(required_values).intersection(age_groups))
        result |= has_traits
        result |= legally_incapable
    return result


def get_study_progress(study, is_end=False):
    if not study:
        return STUDY_PROGRESS_START
    progress = STUDY_PROGRESS_TOTAL / study.proposal.studies_number
    if not is_end:
        progress *= (study.order - 1)
    else:
        progress *= study.order
    return int(STUDY_PROGRESS_START + progress)


def copy_study_to_proposal(proposal, study):
    age_groups = study.age_groups.all()
    traits = study.traits.all()
    compensation = study.compensation
    recruitment = study.recruitment.all()
    intervention = study.intervention if study.has_intervention else None
    observation = study.observation if study.has_observation else None
    sessions = study.session_set.all() if study.has_sessions else []
    surveys = study.survey_set.all()

    s = study
    s.pk = None
    s.proposal = proposal
    s.save()

    s.age_groups = age_groups
    s.traits = traits
    s.compensation = compensation
    s.recruitment = recruitment
    s.save()

    if intervention:
        copy_intervention_to_study(s, intervention)
    if observation:
        copy_observation_to_study(s, observation)
    for session in sessions:
        copy_session_to_study(s, session)

    for survey in surveys:
        copy_survey_to_study(s, survey)


def copy_survey_to_study(study, survey):
    s = survey
    s.pk = None
    s.study = study
    s.save()
