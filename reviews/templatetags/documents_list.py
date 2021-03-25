from django import template
from studies.models import Documents
from collections import OrderedDict

register = template.Library()

@register.inclusion_tag('documents_list.html')
def documents_list(review):
    proposal = review.proposal
    qs = Documents.objects.filter(proposal=proposal)
    
    # From CPython 3.6 dicts should be insertion-ordered anyway
    headers_items = OrderedDict()
    
    headers_items['documents qs'] = [repr(qs)]
    
    for d in qs:
        
        files = [('IC', d.informed_consent),
                 ('Briefing', d.briefing, not d.briefing),
                 ('DIC', d.director_consent_declaration),
                 ('DCI', d.director_consent_information),
                 ('parents_information', d.parents_information, not d.parents_information),
                 ]
        
        headers_items[d] = files
    
    return {'review': review,
            'headers_items': headers_items}
