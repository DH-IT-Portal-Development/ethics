# -*- encoding: utf-8 -*-

from datetime import datetime

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _
from django.utils import timezone

from easy_pdf.rendering import render_to_pdf

from core.utils import AvailableURL, get_secretary
from studies.utils import study_urls


def available_urls(proposal):
    """
    Returns the available URLs for the given Proposal.
    :param proposal: the current Proposal
    :return: a list of available URLs for this Proposal.
    """
    urls = list()

    if proposal.is_pre_assessment:
        urls.append(AvailableURL(url=reverse('proposals:update_pre', args=(proposal.pk,)),
                                 title=_('Algemene informatie over de studie'), margin=0))

        wmo_url = AvailableURL(title=_('Ethische toetsing nodig door een METC?'), margin=0)
        if hasattr(proposal, 'wmo'):
            wmo_url.url = reverse('proposals:wmo_update_pre', args=(proposal.wmo.pk,))
        else:
            wmo_url.url = reverse('proposals:wmo_create_pre', args=(proposal.pk,))
        urls.append(wmo_url)

        submit_url = AvailableURL(title=_('Aanvraag voor voortoetsing klaar voor versturen'), margin=0)
        if hasattr(proposal, 'wmo'):
            submit_url.url = reverse('proposals:submit_pre', args=(proposal.pk,))
        urls.append(submit_url)
    else:
        update_url = 'proposals:update_practice' if proposal.is_practice() else 'proposals:update'
        urls.append(AvailableURL(url=reverse(update_url, args=(proposal.pk,)),
                                 title=_('Algemene informatie over de studie'), margin=0))

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

        submit_url = AvailableURL(title=_('Concept-aanmelding klaar voor versturen'), margin=0)
        if proposal.last_study() and proposal.last_study().is_completed():
            submit_url.url = reverse('proposals:submit', args=(proposal.pk,))
        urls.append(submit_url)

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


def generate_pdf(proposal, template):
    """
    Generates the PDF for a Proposal and attaches it.
    :param proposal: the current Proposal
    :param template: the template for the PDF
    """
    pdf = ContentFile(render_to_pdf(template, {'proposal': proposal}))
    proposal.pdf.save('{}.pdf'.format(proposal.reference_number), pdf)


def end_pre_assessment(proposal):
    """
    Ends the pre-assessment by sending mails to the creator of the Proposal and the secretary,
    and setting the Proposal status to submitted.
    :param proposal: the current Proposal
    """
    secretary = get_secretary()

    proposal.date_submitted = timezone.now()
    proposal.status = proposal.SUBMITTED
    proposal.save()

    subject = _('ETCL: bevestiging indienen aanvraag voor voortoetsing')
    params = {
        'secretary': secretary.get_full_name(),
    }
    msg_plain = render_to_string('mail/pre_assessment_creator.txt', params)
    send_mail(subject, msg_plain, settings.EMAIL_FROM, [proposal.created_by.email])

    subject = _('ETCL: nieuwe aanvraag voor voortoetsing')
    params = {
        'secretary': secretary.get_full_name(),
        'proposal': proposal,
        'proposal_pdf': settings.BASE_URL + proposal.pdf.url,
    }
    msg_plain = render_to_string('mail/pre_assessment_secretary.txt', params)
    msg_html = render_to_string('mail/pre_assessment_secretary.html', params)
    send_mail(subject, msg_plain, settings.EMAIL_FROM, [secretary.email], html_message=msg_html)
