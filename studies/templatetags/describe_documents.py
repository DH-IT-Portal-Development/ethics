from django import template
from studies.models import Documents, Study
from proposals.models import Proposal, Wmo
from observations.models import Observation
from reviews.templatetags.documents_list import give_name
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from django.core.exceptions import ObjectDoesNotExist

register = template.Library()


@register.simple_tag
def describe_file(file):
    """Gives some text describing an uploaded file"""
    
    field_name = file.field.name
    
    nice_name = _('bestand')
    
    if field_name == 'informed_consent':
        nice_name = _('informed consent')
    
    if field_name == 'briefing':
        nice_name = _('informatiebrief')
    
    if field_name == 'director_consent_declaration':
        nice_name = _('informed consent voor de schoolleiding of het departementshoofd')
    
    if field_name == 'director_consent_information':
        nice_name = _('informatiebrief voor de schoolleiding of het departementshoofd')
    
    if field_name == 'parents_information':
        nice_name = _('informatiebrief voor de ouders of verzorgers')
        
    if field_name == 'dmp_file':
        nice_name = _('data management plan')
        
    
    
            
    
    parent = file.instance
    
    if type(parent) is Proposal:
        proposal = parent
    elif type(parent) is Observation:
        proposal = obj.study.proposal
    else:
        proposal = parent.proposal
    
    has_trajectory = False
    
    if type(parent) is Documents:
        has_trajectory = True
        trajectory_name = give_name(parent).lower()
    
    if has_trajectory:
        trajectory_name = trajectory_name.replace('hoofdtraject',
                                                  'het hoofdtraject')
        out_string = _('''
            <i>{}</i> bij <i>{}</i> van studie <i>{}-{}</i>: <i>{}</i>
            ''').format(nice_name.capitalize(),
                         trajectory_name,
                         proposal.reference_number,
                         proposal.reviewing_committee.name,
                         escape(proposal.title),
                         )
    else:
        out_string = _('''
            <i>{}</i> van studie <i>{}-{}</i>: <i>{}</i>
            ''').format(nice_name.capitalize(),
                         proposal.reference_number,
                         proposal.reviewing_committee.name,
                         escape(proposal.title),
                         )
        
    
    return mark_safe(out_string)
