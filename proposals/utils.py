# -*- encoding: utf-8 -*-

from datetime import datetime

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _


class ProposalURL(object):
    def __init__(self, title, margin=0, url=None, is_title=False):
        self.title = title
        self.margin = margin
        self.url = url
        self.is_title = is_title


def available_urls(proposal):
    urls = list()

    urls.append(ProposalURL(url=reverse('proposals:update', args=(proposal.pk,)), title=_('Algemene informatie over de studie'), margin=0))

    wmo_url = ProposalURL(title=_('Ethische toetsing nodig door een METC?'), margin=0)
    if hasattr(proposal, 'wmo'):
        wmo_url.url = reverse('proposals:wmo_update', args=(proposal.wmo.pk,))
    else:
        wmo_url.url = reverse('proposals:wmo_create', args=(proposal.pk,))
    urls.append(wmo_url)

    studies_url = ProposalURL(title=_(u'Eén of meerdere trajecten?'), margin=0)
    if hasattr(proposal, 'wmo'):
        studies_url.url = reverse('proposals:study_start', args=(proposal.pk,))
    urls.append(studies_url)

    for study in proposal.study_set.all():
        urls.extend(study_urls(study))

    if proposal.studies_number > 1:
        urls.append(ProposalURL(title='', is_title=True))

    studies_url = ProposalURL(title=_(u'Concept-aanmelding klaar voor versturen'), margin=0)
    if not proposal.current_study() and proposal.first_study():
        studies_url.url = reverse('proposals:submit', args=(proposal.pk,))
    urls.append(studies_url)

    return urls


def study_urls(study):
    urls = list()

    if study.proposal.studies_number > 1:
        urls.append(ProposalURL(title=_('Traject {} ({})'.format(study.order, study.name)), is_title=True))

    urls.append(ProposalURL(url=reverse('studies:update', args=(study.pk,)), title=_('De deelnemers'), margin=1))

    design_url = ProposalURL(title=_('De onderzoekstype(n)'), margin=1)
    if study.compensation:
        design_url.url = reverse('studies:design', args=(study.pk,))
    urls.append(design_url)

    urls.append(intervention_url(study))
    urls.append(observation_url(study))
    urls.extend(session_urls(study))

    end_url = ProposalURL(title=_('Overzicht en eigen beoordeling van het gehele onderzoek'), margin=1)
    if study.design_completed():
        end_url.url = reverse('studies:session_end', args=(study.pk,))
    urls.append(end_url)

    survey_url = ProposalURL(title=_('Dataverzameling direct betrokkenen t.b.v. het onderzoek'), margin=1)
    if study.design_completed() and study.deception != '':
        survey_url.url = reverse('studies:survey', args=(study.pk,))
    urls.append(survey_url)

    consent_url = ProposalURL(title=_('Informed consent formulieren voor het onderzoek'), margin=1)
    if study.design_completed() and study.has_surveys is not None:
        consent_url.url = reverse('studies:consent', args=(study.pk,))
    urls.append(consent_url)

    return urls


def intervention_url(study):
    result = ProposalURL(title=_('Het interventieonderzoek'), margin=2)
    if study.has_intervention:
        if hasattr(study, 'intervention'):
            result.url = reverse('interventions:update', args=(study.intervention.pk,))
        else:
            result.url = reverse('interventions:create', args=(study.pk,))
    return result


def observation_url(study):
    result = ProposalURL(title=_('Het observatieonderzoek'), margin=2)
    if study.has_observation:
        if hasattr(study, 'observation'):
            result.url = reverse('observations:update', args=(study.observation.pk,))
        else:
            result.url = reverse('observations:create', args=(study.pk,))
    return result


def session_urls(study):
    urls = list()

    tasks_url = ProposalURL(title=_('Het takenonderzoek'), margin=2)

    if study.has_sessions:
        tasks_url.url = reverse('studies:session_start', args=(study.pk,))
    urls.append(tasks_url)

    if study.has_sessions:
        for session in study.session_set.all():
            urls.append(ProposalURL(url=reverse('tasks:start', args=(session.pk,)),
                                    title=_('Het takenonderzoek: sessie {}'.format(session.order)), margin=3))
            for task in session.task_set.all():
                urls.append(ProposalURL(url=reverse('tasks:update', args=(task.pk,)),
                                        title=_('Het takenonderzoek: sessie {} taak {}'.format(session.order, task.order)), margin=3))
            urls.append(ProposalURL(url=reverse('tasks:end', args=(session.pk,)),
                                    title=_('Overzicht van takenonderzoek: sessie {}'.format(session.order)), margin=3))

    return urls


def generate_ref_number(user):
    from .models import Proposal

    current_year = datetime.now().year
    try:
        last_proposal = Proposal.objects.filter(created_by=user).filter(date_created__year=current_year).latest('date_created')
        proposal_number = int(last_proposal.reference_number.split('-')[1]) + 1
    except Proposal.DoesNotExist:
        proposal_number = 1

    return '{}-{:02}-{}'.format(user.username, proposal_number, current_year)
