from django import template
from studies.models import Documents
from collections import OrderedDict

register = template.Library()

@register.inclusion_tag('simple_compare_link')
def simple_compare_link(file):
    pass

@register.inclusion_tag('documents_list.html')
def documents_list(review):
    """This retrieves all files associated with
    a certain review and its proposal and returns them as a
    dict of dicts with display-ready descriptions"""
    
    
    proposal = review.proposal
    
    def give_name(doc):
        """Gets a display name for a Documents object"""
        
        if hasattr(doc, 'study'):
            return "Trajectory {}: {}".format(
                doc.study.order,
                doc.study.name,
                )
        
        for n, d in enumerate(Documents.objects.filter(
            proposal=proposal).filter(
                study=None)):
                
                if doc == d:
                    return "Extra documents {n+1}".format()
    
    
    
    # From Python 3.7 dicts should be insertion-ordered anyway
    # When we upgrade we can let go of OrderedDict 
    headers_items = OrderedDict()    
    
    # Get the proposal PDF
    entries = []
    entries.append(('Proposal PDF', proposal.pdf))
    
    # Pre-approval
    if proposal.pre_approval_pdf:
        entries.append(
            ('Pre-approval', proposal.pre_approval_pdf)
            )
    
    # Pre-assessment
    if proposal.pre_assessment_pdf:
        entries.append(
            ('Pre-assessment', proposal.pre_approval_pdf)
            )
    
    # WMO
    if proposal.wmo and proposal.wmo.status == proposal.wmo.JUDGED:
        entries.append(
            ('METC decision', proposal.wmo.metc_decision_pdf)
            )
    
    headers_items['Proposal'] = entries
    
    # Now get all trajectories / extra documents
    qs = Documents.objects.filter(proposal=proposal)
    
    for d in qs:
        entries = []
        files = [('Informed consent', d.informed_consent),
                 ('Briefing', d.briefing),
                 ('Consent declaratie directeur/departementshoofd', d.director_consent_declaration),
                 ('Consent informatiebrief directeur/departementshoofd', d.director_consent_information),
                 ('Informatiebrief ouders', d.parents_information),
                 ]
        
        for (name, field) in files:
            if field:
                entries.append((name, field))
        
        headers_items[give_name(d)] = entries
    
    return {'review': review,
            'headers_items': headers_items}
