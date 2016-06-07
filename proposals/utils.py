# -*- encoding: utf-8 -*-

from datetime import datetime

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from core.utils import AvailableURL
from studies.utils import study_urls


def available_urls(proposal):
    """
    Returns the available URLs for the given Proposal.
    :param proposal: the current Proposal
    :return: a list of available URLs for this Proposal.
    """
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
    if proposal.last_study() and proposal.last_study().is_completed():
        studies_url.url = reverse('proposals:submit', args=(proposal.pk,))
    urls.append(studies_url)

    return urls


def generate_ref_number(user):
    """
    Generates a reference number for a Proposal.
    :param user: the creator of this Proposal, the currently logged-in User
    :return: a reference number in the format {username}-{nr}-{current_year},
    where nr is the number of Proposals created by the current User in the
    current year.
    """
    from .models import Proposal

    current_year = datetime.now().year
    try:
        last_proposal = Proposal.objects.filter(created_by=user).filter(date_created__year=current_year).latest('date_created')
        proposal_number = int(last_proposal.reference_number.split('-')[1]) + 1
    except Proposal.DoesNotExist:
        proposal_number = 1

    return '{}-{:02}-{}'.format(user.username, proposal_number, current_year)
