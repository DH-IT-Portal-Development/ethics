from django import template
from studies.models import Documents, Study
from proposals.models import Proposal, Wmo
from collections import OrderedDict
from django.urls import reverse

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
        parent_proposal = proposal.parent.pk
    else:
        return reverse()
    
    # Proposals PDF's should pass no attribute
    
    if obj_type == 'proposal':
        return 
    
    # CompareDocumentsView expects the following args:
    # - old pk
    # - new pk
    # - type: wmo, proposal, documents, or observation
    # - attribute (none for Proposal)
    
    pk = proposal.pk
    attribute = file.__name__
    
    
    
    return {'compare_url': url}
    
def give_name(doc):
    """Gets a display name for a Documents object
    
    This string is unique within a proposal, and as such can be used
    for identification purposes.
    """
    
    if hasattr(doc, 'study'):
        return "Trajectory {}: {}".format(
            doc.study.order,
            doc.study.name,
            )
    
    for n, d in enumerate(Documents.objects.filter(
        proposal=proposal).filter(
            study=None)):
            
            if doc == d:
                return "Extra documents {}".format(n+1)

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
                  d.informed_consent, d, 'documents'),
                 ('Briefing',
                  d.briefing, d, 'documents'),
                 ('Consent declaratie directeur/departementshoofd',
                  d.director_consent_declaration, d, 'documents'),
                 ('Consent informatiebrief directeur/departementshoofd',
                  d.director_consent_information, d, 'documents'),
                 ('Informatiebrief ouders',
                  d.parents_information, d, 'documents'),
                 ]
        
        for (name, field) in files:
            if field:
                entries.append((name, field))
        
        headers_items[give_name(d)] = entries
    
    return {'review': review,
            'headers_items': headers_items,
            'proposal': proposal}
