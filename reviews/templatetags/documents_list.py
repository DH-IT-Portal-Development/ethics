from django import template
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.core.exceptions import ObjectDoesNotExist


from main.utils import is_secretary
from studies.models import Documents, Study
from proposals.models import Proposal, Wmo
from proposals.utils.proposal_utils import FilenameFactory
from observations.models import Observation
from collections import OrderedDict


register = template.Library()


@register.inclusion_tag('reviews/simple_compare_link.html')
def simple_compare_link(obj, file):
    """Generates a compare icon"""

    if type(obj) == Proposal:
        proposal = obj
        obj_type = 'proposal'

    elif type(obj) == Wmo:
        obj_type = 'wmo'
        proposal = obj.proposal

    elif type(obj) == Documents:
        obj_type = 'documents'
        proposal = obj.proposal

    elif type(obj) == Observation:
        obj_type = 'observation'
        proposal = obj.study.proposal

    else:
        # Unknown/unsupported type, so we'll stop here
        return {}

    pk = obj.pk
    if proposal.parent:
        parent_proposal = proposal.parent
        parent_pk = parent_proposal.pk
    else:
        # Empty dict will result in empty template
        return {}

    # Get parent documents or observation item.
    # Note that if the parent proposal has a different amount of
    # Trajectories or extra documents this will fail, or compare
    # incorrect documents with each other.
    # Same if the order of trajectories changes.

    if obj_type in ['documents', 'observation']:

        if obj.study:

            try:
                parent_study = parent_proposal.study_set.get(
                    order=obj.study.order
                )

                if obj_type == 'observation':
                    parent_obj = parent_study.observation
                    parent_pk = parent_obj.pk
                else:
                    parent_obj = parent_study.documents
                    parent_pk = parent_obj.pk

            except (ObjectDoesNotExist, AttributeError):
                return {}

        # "Extra" documents
        else:
            for n, d in enumerate(
                proposal.documents_set.filter(study=None)
            ):
                if obj == d:
                    extra_index = n
            try:
                old_set = parent_proposal.documents_set.filter(
                    study=None)
                # Same index, different proposal
                parent_obj = old_set[extra_index]
                parent_pk = parent_obj.pk
            except (IndexError, AttributeError):
                return {}

    # Get parent wmo pk:
    if obj_type == 'wmo':
        parent_obj = parent_proposal.wmo
        parent_pk = parent_obj.pk

    # Set parent object in case of Proposal PDF or DMP
    if obj_type == 'proposal':
        parent_obj = parent_proposal

    # Check that the parent has a comparable object
    if not getattr(parent_obj, file.field.name):
        return {}

    # We now have pk's for the old and new object
    compare_kwargs = {'old': parent_pk,
                      'new': pk,
                      'attribute': file.field.name,
                      }

    # CompareDocumentsView expects the following args:
    # - old pk
    # - new pk
    # - type: wmo, proposal, documents, or observation
    #   > This is hard-coded into the URL, so we handle it here
    # - attribute (none for Proposal PDF)

    if obj_type == 'proposal':
        url = reverse('proposals:compare_proposal_docs', kwargs=compare_kwargs)

    if obj_type == 'wmo':
        url = reverse('proposals:compare_wmo_decision', kwargs=compare_kwargs)

    if obj_type == 'documents':
        url = reverse('proposals:compare_documents', kwargs=compare_kwargs)

    if obj_type == 'observation':
        url = reverse('proposals:compare_observation_approval', kwargs=compare_kwargs)

    return {'compare_url': url}

class DynamicFakeFileField:

    def __init__(self, url, name):

        self.url = url
        self.name = name


def give_name(doc):
    """Gets a display name for a Documents object

    This string is unique within a proposal, and as such can be used
    for identification purposes.
    """

    proposal = doc.proposal

    if doc.study:
        if proposal.study_set.count() == 1:
            return _("Hoofdtraject")
        return mark_safe(
            _("Traject {}: <i>{}</i>").format(
                doc.study.order,
                escape(doc.study.name),
                )
            )

    for n, d in enumerate(Documents.objects.filter(
        proposal=proposal).filter(
            study=None)):

            if doc == d:
                return _("Extra documenten {}").format(n+1)


@register.inclusion_tag('reviews/documents_list.html')
def documents_list(review, user):
    """This retrieves all files associated with
    a certain review and its proposal and returns them as a
    dict of dicts with display-ready descriptions"""

    proposal = review.proposal

    # From Python 3.7 dicts should be insertion-ordered
    # When we upgrade we can let go of OrderedDict
    #
    # Format:
    # headers_items['Header'] = [ ( name, url, owner_object ), ... ]
    # (see template for details)
    headers_items = OrderedDict()

    # Get the proposal PDF
    entries = []
    entries.append(
        # name, file, containing object, comparable
        (_('Aanvraag in PDF-vorm'),
         DynamicFakeFileField(
             reverse('proposals:pdf', args=(proposal.pk,)),
             FilenameFactory('Proposal')(proposal, 'proposal.pdf')),
         proposal, False)
    )

    # Pre-approval
    if proposal.pre_approval_pdf:
        entries.append(
            (_('Eerdere goedkeuring'), proposal.pre_approval_pdf.url, proposal, False)
        )

    # Pre-assessment
    if proposal.pre_assessment_pdf:
        entries.append(
            (_('Aanvraag bij voortoetsing'), proposal.pre_assessment_pdf.url, proposal, False)
        )

    # Data management plan
    if proposal.dmp_file:
        entries.append(
            (_('Data Management Plan'), proposal.dmp_file.url, proposal, True)
        )

    # WMO
    if hasattr(proposal, 'wmo') and proposal.wmo.status == proposal.wmo.JUDGED:
        entries.append(
            (_('Beslissing METC'), proposal.wmo.metc_decision_pdf.url, proposal.wmo, False)
        )

    headers_items[_('Aanmelding')] = {
        'items': entries,
        'edit_link': None,
    }

    # Now get all trajectories / extra documents
    # First we get all objects attached to a study, then we append those
    # without. This way we get the ordering we want.
    qs = Documents.objects.filter(
        proposal=proposal
    ).exclude(study=None) | Documents.objects.filter(
        proposal=proposal, study=None
    )

    for d in qs:
        entries = []
        files = [
            (_('Informed consent'), d.informed_consent, d),
            (_('Informatiebrief'), d.briefing, d),
            (
                _('Consent declaratie directeur/departementshoofd'),
                d.director_consent_declaration,
                d
            ),
            (
                _('Informatiebrief directeur/departementshoofd'),
                d.director_consent_information,
                d
            ),
            (_('Informatiebrief ouders'), d.parents_information, d),
        ]

        # Search for old-style observations (deprecated)
        if d.study and d.study.has_observation:
            if d.study.observation.needs_approval:
                files.append(
                    (
                    _('Toestemmingsdocument observatie'),
                    d.study.observation.approval_document,
                    d.study.observation
                    )
                )

        for (name, field, obj) in files:
            # If it's got a file in it, add an entry
            if field:
                # name, file, containing object, comparable
                entries.append((name, field, obj, True))

        edit_link = None


        if is_secretary(user):
            edit_link = reverse('studies:attachments', args=[d.pk])

        # Get a humanized name for this documents item
        headers_items[give_name(d)] = {
            'items': entries,
            'edit_link': edit_link,
        }

    return {'review': review,
            'headers_items': headers_items,
            'proposal': proposal}
