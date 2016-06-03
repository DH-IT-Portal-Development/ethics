# -*- encoding: utf-8 -*-

from datetime import datetime

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from core.utils import AvailableURL
from interventions.utils import intervention_url
from observations.utils import observation_url
from tasks.utils import session_urls


def available_urls(proposal):
    urls = list()

    urls.append(AvailableURL(url=reverse('proposals:update', args=(proposal.pk,)), title=_('Algemene informatie over de studie'), margin=0))

    wmo_url = AvailableURL(title=_('Ethische toetsing nodig door een METC?'), margin=0)
    if hasattr(proposal, 'wmo'):
        wmo_url.url = reverse('proposals:wmo_update', args=(proposal.wmo.pk,))
    else:
        wmo_url.url = reverse('proposals:wmo_create', args=(proposal.pk,))
    urls.append(wmo_url)

    studies_url = AvailableURL(title=_(u'Eén of meerdere trajecten?'), margin=0)
    if hasattr(proposal, 'wmo'):
        studies_url.url = reverse('proposals:study_start', args=(proposal.pk,))
    urls.append(studies_url)

    prev_study_completed = True
    for study in proposal.study_set.all():
        urls.extend(study_urls(study, prev_study_completed))
        prev_study_completed = study.is_completed()

    if proposal.studies_number > 1:
        urls.append(AvailableURL(title='', is_title=True))

    studies_url = AvailableURL(title=_('Concept-aanmelding klaar voor versturen'), margin=0)
    if proposal.last_study().is_completed():
        studies_url.url = reverse('proposals:submit', args=(proposal.pk,))
    urls.append(studies_url)

    return urls


def study_urls(study, prev_study_completed):
    urls = list()

    if study.proposal.studies_number > 1:
        urls.append(AvailableURL(title=_('Traject {} ({})'.format(study.order, study.name)), is_title=True))

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

    survey_url = AvailableURL(title=_('Dataverzameling direct betrokkenen t.b.v. het onderzoek'), margin=1)
    if study.design_completed() and study.deception != '':
        survey_url.url = reverse('studies:survey', args=(study.pk,))
    urls.append(survey_url)

    consent_url = AvailableURL(title=_('Informed consent formulieren voor het onderzoek'), margin=1)
    if study.design_completed() and study.has_surveys is not None:
        consent_url.url = reverse('studies:consent', args=(study.pk,))
    urls.append(consent_url)

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
