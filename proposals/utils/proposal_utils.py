# -*- encoding: utf-8 -*-

from collections import defaultdict
from datetime import datetime
from io import BytesIO
import os

from django.conf import settings
from django.contrib.staticfiles import finders
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage
from django.core.mail import send_mail
from django.db.models import Q
from django.urls import reverse
from django.template.loader import render_to_string
from django.utils.translation import activate, get_language, ugettext as _
from django.utils.deconstruct import deconstructible

from main.utils import AvailableURL, get_secretary
from studies.utils import study_urls


__all__ = ['available_urls', 'generate_ref_number',
           'generate_revision_ref_number', 'generate_pdf',
           'check_local_facilities', 'notify_local_staff',
           'FilenameFactory', 'OverwriteStorage',
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
                                 title=_('Algemene informatie over de aanvraag')))

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
                                 title=_('Algemene informatie over de aanvraag')))

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

        consent_docs_url = AvailableURL(
            title=_('Uploaden'), 
            url=reverse(
                'proposals:consent', 
                args=(proposal.pk, )
                )
            )
        translated_docs_url = AvailableURL(
            title=_('Vertaling'), 
            url=reverse(
                'proposals:translated', 
                args=(proposal.pk, )
                )
            )
        consent_url = AvailableURL(
            title=_('Formulieren'), 
            children=[
                translated_docs_url, 
                consent_docs_url
                ]
            )

        data_management_url = AvailableURL(title=_('Datamanagement'))
        submit_url = AvailableURL(title=_('Versturen'))

        if proposal.last_study() and proposal.last_study().is_completed():
            consent_url.url = reverse('proposals:translated', args=(proposal.pk, ))
            data_management_url.url = reverse('proposals:data_management', args=(proposal.pk, ))
            submit_url.url = reverse('proposals:submit', args=(proposal.pk,))

        if proposal.translated_forms is not None:
            consent_url.url = reverse('proposals:consent', args=(proposal.pk,))

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
            reference_number__startswith="{}-".format(str(current_year)[2:])
        ).order_by('-reference_number').first()

        if not last_proposal:
            return 1

        _, num, _ = last_proposal.reference_number.split('-', maxsplit=2)

        return int(num) + 1
    except Proposal.DoesNotExist:
        return 1

def generate_pdf(proposal, template=False):
    """Grandfathered function for pdf saving. The template arg currently
    only exists for backwards compatibility."""

    from proposals.views.proposal_views import ProposalAsPdf

    view = ProposalAsPdf()
    view.object = proposal

    # Note, this is where the _view_ decides what kind of proposal it is
    # and chooses the appropriate template.
    context = view.get_context_data()

    with BytesIO() as f:
        view.get_pdf_response(
            context,
            dest=f,
        )
        pdf = ContentFile(f.getvalue())
    proposal.pdf.save(view.get_pdf_filename(), pdf)

    return proposal.pdf

def pdf_link_callback(uri, rel):
    """
    Convert HTML URIs to absolute system paths so xhtml2pdf can access those
    resources

    Retrieved from xhtml2pdf docs
    """
    result = finders.find(uri)
    if result:
        if not isinstance(result, (list, tuple)):
            result = [result]
        result = list(os.path.realpath(path) for path in result)
        path=result[0]
    else:
        sUrl = settings.STATIC_URL        # Typically /static/
        sRoot = settings.STATIC_ROOT      # Typically /home/userX/project_static/
        mUrl = settings.MEDIA_URL         # Typically /media/
        mRoot = settings.MEDIA_ROOT       # Typically /home/userX/project_static/media/

        if uri.startswith(mUrl):
            path = os.path.join(mRoot, uri.replace(mUrl, ""))
        elif uri.startswith(sUrl):
            path = os.path.join(sRoot, uri.replace(sUrl, ""))
        else:
            return uri

    # make sure that file exists
    if not os.path.isfile(path):
        raise Exception(
            'media URI must start with %s or %s' % (sUrl, mUrl)
        )
    return path


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

    if proposal.is_revision:
        subject = _('FETC-GW: gereviseerde aanvraag gebruikt labfaciliteiten')
    else:
        subject = _('FETC-GW: nieuwe aanvraag gebruikt labfaciliteiten')

    params = {
        'secretary': secretary.get_full_name(),
        'proposal': proposal,
        'applicants': [applicant.get_full_name() for applicant in proposal.applicants.all()],
        'facilities': sorted(check_local_facilities(proposal).items()),
        'is_revision': proposal.is_revision,
    }
    msg_plain = render_to_string('mail/local_staff_notify.txt', params)
    send_mail(subject, msg_plain, settings.EMAIL_FROM, [settings.EMAIL_LOCAL_STAFF])

    # Reset the current language
    activate(current_language)


@deconstructible
class FilenameFactory:
    '''A callable class which can be passed to upload_to() in FileFields
    and can be deconstructed for migrations'''

    def __init__(self, document_type):

        # document_type is a string describing the document kind,
        # such as "Informed_Consent"
        self.document_type = document_type

    def __call__(self, instance, original_fn):
        '''Returns a custom filename preserving the original extension,
        something like "FETC-2020-002-01-Villeneuve-T2-Informed-Consent.pdf"'''

        # Importing here to prevent circular import
        from proposals.models import Proposal, Wmo

        if isinstance(instance, Proposal):
            # This is a proposal PDF
            proposal = instance
            trajectory = None
        elif isinstance(instance, Wmo):
            # This is an METC decision file
            proposal = instance.proposal
            trajectory = None
        else:
            # In case of Documents objects
            proposal = instance.proposal
            try:
                trajectory = 'T' + str(instance.study.order)
            except AttributeError:
                # No associated study, so this is an extra Documents instance
                # We need to give it an index so they don't overwrite each other
                extra_index = 1

                # Again, to prevent circular imports
                from studies.models import Documents
                qs = Documents.objects.filter(
                    proposal=proposal).filter(
                        study=None)

                for docs in qs:
                    # The current Documents instance might not yet be saved and
                    # therefore not exist in the QS. Hence the for loop instead of
                    # the more traditional while
                    if docs == instance:
                        break # i.e. this may never happen
                    extra_index += 1

                # Unknown
                trajectory = 'Extra' + str(extra_index)

        chamber = proposal.reviewing_committee.name
        lastname = proposal.created_by.last_name
        refnum = proposal.reference_number

        extension = '.' + original_fn.split('.')[-1][-7:] # At most 7 chars seems reasonable

        fn_parts = ['FETC',
                    chamber,
                    refnum,
                    lastname,
                    trajectory,
                    self.document_type,
                    ]

        def not_empty(item):
            if item == None:
                return False
            if str(item) == '':
                return False
            return True

        # Translations will trip up join(), so we convert them here
        fn_parts = [str(p) for p in filter(not_empty, fn_parts)]

        return '-'.join(fn_parts) + extension


class OverwriteStorage(FileSystemStorage):

    def get_available_name(self, name, **kwargs):
        """Returns a filename that's free on the target storage system, and
        available for new content to be written to.

        Modified from http://djangosnippets.org/snippets/976/
        """
        import os

        # If the filename already exists, remove it
        if self.exists(name):
            os.remove(os.path.join(settings.MEDIA_ROOT, name))
        return super(OverwriteStorage, self).get_available_name(name, **kwargs)
