# -*- encoding: utf-8 -*-

from collections import defaultdict
from datetime import datetime

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.mail import send_mail
from django.urls import reverse
from django.template.loader import render_to_string
from django.utils.translation import activate, get_language, ugettext as _

from easy_pdf.rendering import render_to_pdf

from core.utils import AvailableURL, get_secretary
from studies.utils import study_urls

__all__ = ['available_urls', 'generate_ref_number', 'generate_pdf',
           'check_local_facilities', 'notify_local_staff']


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
    elif proposal.is_pre_approved:
        urls.append(AvailableURL(url=reverse('proposals:update_pre_approved', args=(proposal.pk,)),
                                 title=_('Algemene informatie over de studie'), margin=0))

        submit_url = AvailableURL(
            title=_('Aanvraag voor voortoetsing klaar voor versturen'),
            margin=0,
            url = reverse('proposals:submit_pre_approved', args=(proposal.pk,))
        )
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

        consent_url = AvailableURL(title=_('Informed consent formulieren'), margin=0)
        data_management_url = AvailableURL(title=_('Datamanagement'), margin=0)
        submit_url = AvailableURL(title=_('Concept-aanmelding klaar voor versturen'), margin=0)

        if proposal.last_study() and proposal.last_study().is_completed():
            consent_url.url = reverse('proposals:consent', args=(proposal.pk,))
            data_management_url.url = reverse('proposals:data_management', args=(proposal.pk, ))
            submit_url.url = reverse('proposals:submit', args=(proposal.pk,))

        urls.append(consent_url)
        urls.append(data_management_url)
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
    from ..models import Proposal

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
    # Local import, as otherwise a circular import will happen because the proposal model imports this file
    # (And the document model imports the proposal model)
    from studies.models import Documents

    # Change language to English for this PDF, but save the current language to reset it later
    current_language = get_language()
    activate('en')

    documents = {
        'extra': []
    }

    for document in Documents.objects.filter(proposal=proposal).all():
        if document.study:
            documents[document.study.pk] = document
        else:
            documents['extra'].append(document)

    # This try catch does not actually handle any errors. It only makes sure the language is properly reset before
    # reraising the exception.
    try:
        context = {'proposal': proposal, 'BASE_URL': settings.BASE_URL, 'documents': documents}
        pdf = ContentFile(render_to_pdf(template, context))
        proposal.pdf.save('{}.pdf'.format(proposal.reference_number), pdf)
    except Exception as e:
        activate(current_language)
        raise e

    # Reset the current language
    activate(current_language)


def check_local_facilities(proposal):
    """
    Checks whether local lab facilities are used in the given Proposal
    :param proposal: the current Proposal
    :return: an empty dictionary if no local support is needed, a dictionary with local facilities otherwise
    """
    result = defaultdict(set)

    def add_to_result(model):
        result[model._meta.verbose_name].add(model.description)

    for study in proposal.study_set.all():
        for recruitment in study.recruitment.all():
            if recruitment.is_local:
                add_to_result(recruitment)

        if study.has_intervention:
            for setting in study.intervention.setting.all():
                if setting.is_local:
                    add_to_result(setting)
        if study.has_observation:
            for setting in study.observation.setting.all():
                if setting.is_local:
                    add_to_result(setting)
        if study.has_sessions:
            for session in study.session_set.all():
                for setting in session.setting.all():
                    if setting.is_local:
                        add_to_result(setting)

                for task in session.task_set.all():
                    for registration in task.registrations.all():
                        if registration.is_local:
                            add_to_result(registration)

    return result


def notify_local_staff(proposal):
    """
    Notifies local lab staff of the current Proposal via e-mail.
    :param proposal: the current Proposal
    """
    # Change language to Dutch for this e-mail, but save the current language to reset it later
    current_language = get_language()
    activate('nl')

    secretary = get_secretary()

    subject = _('FETC-GW: nieuwe studie ingediend')
    params = {
        'secretary': secretary.get_full_name(),
        'proposal': proposal,
        'applicants': [applicant.get_full_name() for applicant in proposal.applicants.all()],
        'facilities': sorted(check_local_facilities(proposal).items()),
    }
    msg_plain = render_to_string('mail/local_staff_notify.txt', params)
    send_mail(subject, msg_plain, settings.EMAIL_FROM, [settings.EMAIL_LOCAL_STAFF])

    # Reset the current language
    activate(current_language)
