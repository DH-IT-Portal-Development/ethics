from django import template

from main.utils import is_secretary
from studies.models import Documents, Study
from proposals.models import Proposal, Wmo
from observations.models import Observation
from collections import OrderedDict
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.utils.html import escape
from django.utils.safestring import mark_safe

from django.core.exceptions import ObjectDoesNotExist

from proposals.utils.proposal_utils import FilenameFactory

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



class Container:

    def __init__(self, header, **kwargs):

        self.edit_link = False
        self.header = header
        self.items = []

        self.__dict__.update(kwargs)



class DocItem:

    def __init__(self, name, **kwargs):

        self.name = name
        self.comparable = False
        self.filename = None
        self.link_url = None

        self.__dict__.update(kwargs)

    def get_filename(self):

        if self.filename:
            return self.filename

        return self.field.name

    def get_link_url(self):

        if self.link_url:
            return self.link_url

        return self.field.url



@register.inclusion_tag('reviews/documents_list.html')
def documents_list(review, user):
    """This retrieves all files associated with
    a certain review and its proposal and returns them as a
    list of Container objects"""

    proposal = review.proposal
    containers = []

    # Get the proposal PDF
    pdf_container = Container(_('Aanmelding'))

    proposal_pdf = DocItem(_('Aanvraag in PDF-vorm'))
    proposal_pdf.link_url = reverse('proposals:pdf', args=(proposal.pk,))

    # Because the pdf is generated on the spot, we need to
    # generate the filename here too
    proposal_pdf.filename = FilenameFactory('Proposal')(
        proposal, 'proposal.pdf') # Original filename is just to determine
                                  # the extension

    pdf_container.items.append(proposal_pdf)

    # Pre-approval
    if proposal.pre_approval_pdf:

        pre_approval = DocItem(_('Eerdere goedkeuring'))
        pre_approval.field = proposal.pre_approval_pdf

        pdf_container.items.append(pre_approval)

    # Pre-assessment
    if proposal.pre_assessment_pdf:

        pre_assessment = DocItem(_('Aanvraag bij voortoetsing'))
        pre_assessment.field = proposal.pre_assessment_pdf

        pdf_container.items.append(pre_assessment)


    # Data management plan
    if proposal.dmp_file:

        dmp_file = DocItem(_('Data Management Plan'))
        dmp_file.field = proposal.dmp_file

        pdf_container.items.append(dmp_file)

    # WMO
    if hasattr(proposal, 'wmo') and proposal.wmo.status == proposal.wmo.JUDGED:

        metc_decision = DocItem(_('Beslissing METC'))
        metc_decision.field = proposal.wmo.metc_decision_pdf

        pdf_container.items.append(metc_decision)

    # Finally, append the container
    containers.append(pdf_container)

    # Now get all trajectories / extra documents
    # First we get all objects attached to a study, then we append those
    # without. This way we get the ordering we want.
    qs = Documents.objects.filter(
        proposal=proposal
    ).exclude(study=None) | Documents.objects.filter(
        proposal=proposal, study=None
    )

    for d in qs:

        # Get a humanized name and create container item
        documents_container = Container(give_name(d))

        # We create a list of possible files
        # with the format [(Name, FileField, Containing object)...]
        potential_files = [
            (_('Informed consent'), d.informed_consent, d),
            (_('Informatiebrief'), d.briefing, d),
            ( _('Consent declaratie directeur/departementshoofd'),
                d.director_consent_declaration, d),
            (_('Informatiebrief directeur/departementshoofd'),
                d.director_consent_information, d),
            (_('Informatiebrief ouders'), d.parents_information, d),
        ]

        # Search for old-style observations (deprecated)
        if d.study and d.study.has_observation:
            if d.study.observation.needs_approval:
                potential_files.append(
                    (
                    _('Toestemmingsdocument observatie'),
                    d.study.observation.approval_document,
                    d.study.observation
                    )
                )

        # We then iterate over potential files for every Documents object in the QS
        for (name, field, obj) in potential_files:
            # If it's got a file in it, add an item to this container
            if field:
                item = DocItem(name)
                item.comparable = True
                item.field = field
                item.object = obj
                documents_container.items.append(item)

        # Only the secretary gets an edit link
        if is_secretary(user):
            documents_container.edit_link = reverse('studies:attachments', args=[d.pk])

        containers.append(documents_container)

    # Finally, return template context
    return {'review': review,
            'containers': containers,
            'proposal': proposal}
