from django import template
from studies.models import Documents, Study
from proposals.models import Proposal, Wmo
from collections import OrderedDict
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

register = template.Library()

@register.inclusion_tag('simple_compare_link.html')
def simple_compare_link(obj, file):
    """Generates a compare icon"""
    
    if type(obj) == Proposal:
        proposal = obj
        obj_type = 'proposal'
    else:
        proposal = obj.proposal
    
    if type(obj) == Wmo:
        obj_type = 'wmo'
    
    if type(obj) == Documents:
        obj_type = 'documents'
    
    # Observations are currently unhandled
    
    pk = obj.pk
    if proposal.parent:
        parent_proposal = proposal.parent
        parent_pk = parent_proposal.pk
    else:
        # Empty dict will result in empty template
        return {}
    
    # Get parent documents item.
    # Note that if the parent proposal has a different amount of
    # Trajectories or extra documents this will fail.
    # Same if the order of trajectories changes.
    if obj_type == 'documents':
        # Study documents
        if obj.study:
            parent_study = parent_proposal.study_set.get(
                order=obj.study.order)
            parent_pk = parent_study.pk
        # "Extra" documents
        else:
            for n, d in enumerate(proposal.documents_set.filter(
                study=None)):
                    if obj == d:
                        extra_index = n
            try:
                old_set = parent_proposal.documents_set.filter(
                    study=None)
                # Same index, different proposal
                parent_pk = old_set[extra_index].pk
            except (IndexError, AttributeError):
                return {}
    
    # Get parent wmo pk:
    if obj_type == 'wmo':
        parent_pk = parent_proposal.wmo.pk
    
    # We now have pk's for the old and new object
    compare_kwargs = {'old': parent_pk,
                      'new': pk,
                      }
    
    # Otherwise, add the attribute
    compare_kwargs['attribute'] = file.field.name
    
    # CompareDocumentsView expects the following args:
    # - old pk
    # - new pk
    # - type: wmo, proposal, documents, or observation
    #   > This is hard-coded into the URL, so we handle it here
    # - attribute (none for Proposal PDF)
    
    if obj_type == 'proposal':
        url= reverse('proposals:compare_proposal_docs', kwargs=compare_kwargs)
    
    if obj_type == 'wmo':
        url= reverse('proposals:compare_wmo_decision', kwargs=compare_kwargs)
    
    if obj_type == 'documents':
        url= reverse('proposals:compare_documents', kwargs=compare_kwargs)
    
    return {'compare_url': url}
    
def give_name(doc):
    """Gets a display name for a Documents object
    
    This string is unique within a proposal, and as such can be used
    for identification purposes.
    """
    
    proposal=doc.proposal
    
    if doc.study:
        if proposal.study_set.count() == 1:
            return _("Hoofdtraject")
        return _("Traject {}: {}").format(
            doc.study.order,
            doc.study.name,
            )
    
    for n, d in enumerate(Documents.objects.filter(
        proposal=proposal).filter(
            study=None)):
            
            if doc == d:
                return _("Extra documenten {}").format(n+1)

@register.inclusion_tag('documents_list.html')
def documents_list(review):
    """This retrieves all files associated with
    a certain review and its proposal and returns them as a
    dict of dicts with display-ready descriptions"""
    
    proposal = review.proposal
    

    
    # From Python 3.7 dicts should be insertion-ordered
    # When we upgrade we can let go of OrderedDict 
    headers_items = OrderedDict()    
    
    # Get the proposal PDF
    entries = []
    entries.append(('Proposal PDF', proposal.pdf, proposal, 'proposal'))
    
    # Pre-approval
    if proposal.pre_approval_pdf:
        entries.append(
            ('Pre-approval', proposal.pre_approval_pdf, proposal, 'proposal')
            )
    
    # Pre-assessment
    if proposal.pre_assessment_pdf:
        entries.append(
            ('Pre-assessment', proposal.pre_approval_pdf, 'pre_assessment_pdf')
            )
    
    # WMO
    if proposal.wmo and proposal.wmo.status == proposal.wmo.JUDGED:
        entries.append(
            ('METC decision', proposal.wmo.metc_decision_pdf, proposal.wmo, 'wmo')
            )
    
    headers_items['Proposal'] = entries
    
    # Now get all trajectories / extra documents
    qs = Documents.objects.filter(proposal=proposal)
    
    for d in qs:
        entries = []
        files = [('Informed consent',
                  d.informed_consent, d),
                 ('Briefing',
                  d.briefing, d),
                 ('Consent declaratie directeur/departementshoofd',
                  d.director_consent_declaration, d),
                 ('Informatiebrief directeur/departementshoofd',
                  d.director_consent_information, d),
                 ('Informatiebrief ouders',
                  d.parents_information, d),
                 ]
        
        for (name, field, obj) in files:
            if field:
                entries.append((name, field, obj))
        
        headers_items[give_name(d)] = entries
    
    return {'review': review,
            'headers_items': headers_items,
            'proposal': proposal}
