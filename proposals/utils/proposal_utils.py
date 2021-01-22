# -*- encoding: utf-8 -*-

from collections import defaultdict
from datetime import datetime

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage
from django.core.mail import send_mail
from django.db.models import Q
from django.urls import reverse
from django.template.loader import render_to_string
from django.utils.translation import activate, get_language, ugettext as _

from easy_pdf.rendering import render_to_pdf

from main.utils import AvailableURL, get_secretary
from studies.utils import study_urls

__all__ = ['available_urls', 'generate_ref_number',
           'generate_revision_ref_number', 'generate_pdf',
           'check_local_facilities', 'notify_local_staff',
           'filename_factory', 'OverwriteStorage',
           ]


def available_urls(proposal):
    """
    Returns the available URLs for the given Proposal.
    :param proposal: the current Proposal
    :return: a list of available URLs for this Proposal.
    """
    urls = list()

    if proposal.is_pre_assessment:
        urls.append(AvailableURL(url=reverse('proposals:update_pre', args=(proposal.pk,)),
                                 title=_('Algemene informatie over de studie')))

        wmo_url = AvailableURL(title=_('Ethische toetsing nodig door een METC?'))
        if hasattr(proposal, 'wmo'):
            wmo_url.url = reverse('proposals:wmo_update_pre', args=(proposal.wmo.pk,))
        else:
            wmo_url.url = reverse('proposals:wmo_create_pre', args=(proposal.pk,))
        urls.append(wmo_url)

        submit_url = AvailableURL(title=_('Aanvraag voor voortoetsing klaar voor versturen'))
        if hasattr(proposal, 'wmo'):
            submit_url.url = reverse('proposals:submit_pre', args=(proposal.pk,))
        urls.append(submit_url)
    elif proposal.is_pre_approved:
        urls.append(AvailableURL(url=reverse('proposals:update_pre_approved', args=(proposal.pk,)),
                                 title=_('Algemene informatie over de studie')))

        submit_url = AvailableURL(
            title=_('Aanvraag voor voortoetsing klaar voor versturen'),
            margin=0,
            url = reverse('proposals:submit_pre_approved', args=(proposal.pk,))
        )
        urls.append(submit_url)
    else:
        update_url = 'proposals:update_practice' if proposal.is_practice() else 'proposals:update'
        urls.append(
            AvailableURL(
                url=reverse(update_url, args=(proposal.pk,)),
                title=_('Algemeen'),
            )
        )

        wmo_url = AvailableURL(
            title=_('METC')
        )
        if hasattr(proposal, 'wmo'):
            wmo_url.url = reverse(
                'proposals:wmo_update',
                args=(proposal.wmo.pk,)
            )
        else:
            wmo_url.url = reverse(
                'proposals:wmo_create',
                args=(proposal.pk,)
            )
        urls.append(wmo_url)

        studies_url = AvailableURL(title=_('Trajecten'))
        if hasattr(proposal, 'wmo'):
            studies_url.url = reverse(
                        'proposals:study_start',
                        args=(proposal.pk,)
                    )

            if proposal.study_set.count() > 0:
                _add_study_urls(studies_url, proposal)

            urls.append(studies_url)


        consent_url = AvailableURL(title=_('Documenten'))
        data_management_url = AvailableURL(title=_('Datamanagement'))
        submit_url = AvailableURL(title=_('Versturen'))

        if proposal.last_study() and proposal.last_study().is_completed():
            consent_url.url = reverse('proposals:consent', args=(proposal.pk,))
            data_management_url.url = reverse('proposals:data_management', args=(proposal.pk, ))
            submit_url.url = reverse('proposals:submit', args=(proposal.pk,))

        urls.append(consent_url)
        urls.append(data_management_url)
        urls.append(submit_url)

    return urls


def _add_study_urls(main_element, proposal):
    # If only one trajectory, add the children urls of that study directly.
    # (Bypassing the study's own node)
    if proposal.studies_number == 1:
        main_element.children.extend(
            study_urls(proposal.study_set.first(), True).children
        )
        return

    # Otherwise, add them all with the parent node
    prev_study_completed = True
    for study in proposal.study_set.all():
        main_element.children.append(
            study_urls(study, prev_study_completed)
        )
        prev_study_completed = study.is_completed()


def generate_ref_number():
    """
    Generates a reference number for a new(!) Proposal.
    NOTE: Use generate_revision_ref_number to create reference numbers for
    revisions! This function will always create a new ref.num. with version = 1
    :return: a reference number in the format {nr}-{vr}-{current_year},
    where nr is the number of Proposals created  in the current year excluding
    revisions. Vr is the version of this proposal, this function will always return vr = 1.
    """
    # Set default values
    current_year = datetime.now().year
    current_year_formatted = str(current_year)[2:]
    proposal_number = _get_next_proposal_number(current_year)
    version_number = 1

    return '{}-{:03}-{:02}'.format(
        current_year_formatted,
        proposal_number,
        version_number,
    )


def generate_revision_ref_number(parent):
    """
    Generates a new reference number for revisions of a proposal.
    This is done by looking up the last revision of the specified proposal,
    not by incrementing the version of the specified proposal.
    (The latter will fail spectacularly when a user makes 2 revisions from the
    same proposal)
    Note: this function uses two helper functions
    :param parent: The proposal that will be revised
    :return: a reference number in the format {year}-{nr}-{vr}, where nr is the
    number of Proposals created by the current User in the current year
    excluding revisions. This method will use the same nr as the parent. Vr
    is the version of this proposal, this function
    will use the next available version number (this might not be the same as
    parent.vr + 1, as that one might already exist).
    """
    parent_parts = parent.reference_number.split('-')

    # If we have 4 parts, the ref.number is in the user-nr-vr-year format
    if len(parent_parts) == 4:
        return _generate_revision_ref_number_oldformat(parent, 2)
    # If the first part is longer than 2 characters, it's the usr-nr-year format
    elif len(parent_parts[0]) > 2:
        # Otherwise, we assume it's in the old user-nr-year format
        return _generate_revision_ref_number_oldformat(parent, 1)

    return _generate_revision_ref_number_newformat(parent)


def _generate_revision_ref_number_oldformat(parent, version):
    """This method generates a new reference number from proposals using
    an older version of the ref.num.
    """
    from ..models import Proposal

    parent_parts = parent.reference_number.split('-')

    old_proposal_number = int(parent_parts[1])
    proposal_number = -1
    year = -1

    # Version 2 is the user-nr-vr-year format
    if version == 2:
        year = parent_parts[3]
        proposal_number = _get_next_proposal_number(int(year))
    # Version 1 is the usr-nr-year format
    elif version == 1:
        # Otherwise, we assume it's in the old user-nr-year format
        year = parent_parts[2]
        proposal_number = _get_next_proposal_number(int(year))

    username = parent.created_by.username

    # Count all proposals by matching all proposals with the same user-nr
    # part and the same year. (This way we find both old and new style ref.nums)
    num_versions = Proposal.objects.filter(
        Q(
            reference_number__istartswith="{}-{:02}".format(username,
                                                            old_proposal_number),
            reference_number__endswith=str(year)
        ) | Q(reference_number__istartswith="{}-{:03}".format(year,
                                                              proposal_number))

    ).count()

    # The new revision is number of current versions + 1
    version_number = num_versions + 1

    return '{}-{:03}-{:02}'.format(
        year[2:],
        proposal_number,
        version_number,
    )


def _generate_revision_ref_number_newformat(parent):
    """This method generates a new reference number from proposals using
    the current version of the ref.num.
    """
    from ..models import Proposal

    parent_parts = parent.reference_number.split('-')
    year = int(parent_parts[0])
    proposal_number = int(parent_parts[1])

    # Get all proposals with this reference number (excluding version number)
    parent_proposals = Proposal.objects.filter(
        reference_number__istartswith="{}-{:03}".format(year, proposal_number)
    )

    # Loop through all them, and note the newest version seen
    newest = None
    for parent_proposal in parent_proposals:
        version = parent_proposal.reference_number.split('-')[2]
        version = int(version)
        if not newest or version > newest:
            newest = version

    version_number = newest + 1

    return '{}-{:03}-{:02}'.format(
        year,
        proposal_number,
        version_number,
    )


def _get_next_proposal_number(current_year) -> int:
    from ..models import Proposal

    try:
        # We count all proposals for this year by selecting all proposals
        # with a reference number ending with the current year.
        last_proposal = Proposal.objects.filter(
            reference_number__startswith="{}-".format(str(current_year)[:2])
        ).order_by('-reference_number').first()

        if not last_proposal:
            return 1

        _, num, _ = last_proposal.reference_number.split('-', maxsplit=2)

        return int(num) + 1
    except Proposal.DoesNotExist:
        return 1


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

def filename_factory(document_type):
    'Returns a filename generator for a given document_type'
    
    def mkfn(instance, original_fn):
        '''Returns a custom filename preserving the original extension,
        something like "FETC-2020-002-01-Villeneuve-T2-Informed-Consent.pdf"
        
        Note: this function absolutely expects an instance.proposal'''
        
        # Importing here to prevent circular import
        from proposals.models import Proposal
        
        if isinstance(instance, Proposal):
            proposal = instance
        else:
            # In case of Documents or Study objects
            proposal = instance.proposal
            try:
                trajectory = 'T' + str(instance.study.id)
            except AttributeError:
                trajectory = None
        
        lastname = proposal.created_by.last_name
        refnum = proposal.reference_number
        
        extension = '.' + original_fn.split('.')[-1][-7:] # At most 7 chars seems reasonable
        
        fn_parts = [ p for p in ['FETC',
                                 refnum,
                                 lastname,
                                 trajectory,
                                 document_type,
                                 ] if p != None or '' ]
        
        return '-'.join(fn_parts) + extension 
    
    return mkfn


class OverwriteStorage(FileSystemStorage):

    def get_available_name(self, name, **kwargs):
        """Returns a filename that's free on the target storage system, and
        available for new content to be written to.

        Modified from http://djangosnippets.org/snippets/976/

        This file storage solves overwrite on upload problem. Another
        proposed solution was to override the save method on the model
        like so (from https://code.djangoproject.com/ticket/11663):

        def save(self, *args, **kwargs):
            try:
                this = MyModelName.objects.get(id=self.id)
                if this.MyImageFieldName != self.MyImageFieldName:
                    this.MyImageFieldName.delete()
            except: pass
            super(MyModelName, self).save(*args, **kwargs)
        """
        import os
        
        # If the filename already exists, remove it
        if self.exists(name):
            os.remove(os.path.join(settings.MEDIA_ROOT, name))
        return super(OverwriteStorage, self).get_available_name(name, **kwargs)
