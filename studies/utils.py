from __future__ import division

from django.urls import reverse
from django.utils.translation import ugettext as _

from core.utils import AvailableURL
from interventions.utils import intervention_url, copy_intervention_to_study
from observations.utils import observation_url, copy_observation_to_study
from tasks.utils import session_urls, copy_session_to_study

STUDY_PROGRESS_START = 10
STUDY_PROGRESS_TOTAL = 90


def check_has_adults(selected_age_groups):
    """
    Checks whether the given AgeGroups include adults.
    """
    from .models import AgeGroup

    adult_age_groups = AgeGroup.objects.filter(is_adult=True).values_list('id', flat=True)
    return bool(set(selected_age_groups).intersection(adult_age_groups))


def check_necessity_required(proposal, age_groups, has_traits, legally_incapable):
    """
    This call checks whether the necessity questions are required. They are required when:
    - The researcher requires a supervisor AND one of these cases applies:
    * A selected AgeGroup requires details.
    * Participants have been selected on certain traits.
    * Participants are legally incapable.
    """
    from .models import AgeGroup

    if proposal.relation and not proposal.relation.needs_supervisor:
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


def study_urls(study, prev_study_completed):
    """
    Returns the available URLs for the current Study.
    :param study: the current Study
    :param prev_study_completed: whether the previous Study is completed
    :return: a list of available URLs for this Study.
    """
    urls = list()

    if study.proposal.studies_number > 1:
        urls.append(AvailableURL(title=_('Traject {} ({})').format(study.order, study.name), is_title=True))

    study_url = AvailableURL(title=_('De deelnemers'), margin=1)
    study_url.url = reverse('studies:update', args=(study.pk,))
    if prev_study_completed:
        urls.append(study_url)

    design_url = AvailableURL(title=_('De onderzoekstype(n)'), margin=1)
    if study.compensation:
        design_url.url = reverse('studies:design', args=(study.pk,))
    urls.append(design_url)

    urls.append(intervention_url(study))
    urls.append(observation_url(study))
    urls.extend(session_urls(study))

    end_url = AvailableURL(title=_('Overzicht en eigen beoordeling van het gehele onderzoek'), margin=1)
    if study.design_completed():
        end_url.url = reverse('studies:design_end', args=(study.pk,))
    urls.append(end_url)

    return urls

def create_documents_for_study(study):
    from .models import Documents

    d = Documents()
    d.proposal = study.proposal
    d.study = study
    d.save()


def copy_study_to_proposal(proposal, study):
    """
    Copies the given Study to the given Proposal.
    :param proposal: the current Proposal
    :param study: the current Study
    :return: the Proposal appended with the details of the given Study.
    """
    old_pk = study.pk
    age_groups = study.age_groups.all()
    traits = study.traits.all()
    compensation = study.compensation
    recruitment = study.recruitment.all()
    intervention = study.intervention if study.has_intervention else None
    observation = study.observation if study.has_observation else None
    sessions = study.session_set.all() if study.has_sessions else []

    s = study
    s.pk = None
    s.proposal = proposal
    s.save()

    s.age_groups.set(age_groups)
    s.traits.set(traits)
    s.compensation = compensation
    s.recruitment.set(recruitment)
    s.save()

    if intervention:
        copy_intervention_to_study(s, intervention)
    if observation:
        copy_observation_to_study(s, observation)
    for session in sessions:
        copy_session_to_study(s, session)

    copy_documents_to_study(old_pk, s)

def copy_documents_to_study(study_old, study):
    from .models import Documents

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