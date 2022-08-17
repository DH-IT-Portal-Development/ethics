from typing import Optional

from django import template
from django.utils.translation import gettext_lazy as _

from interventions.models import Intervention
from observations.models import Observation
from proposals.models import Proposal, Wmo
from studies.models import Documents, Study
from tasks.models import Session, Task

register = template.Library()


def _get_proposal_object(obj) -> Optional[Proposal]:
    if type(obj) == Proposal:
        return obj
    elif type(obj) == Wmo:
        return obj.proposal
    elif type(obj) == Documents:
        return obj.proposal
    elif type(obj) == Observation:
        return obj.study.proposal
    elif type(obj) == Intervention:
        return obj.study.proposal
    elif type(obj) == Session:
        return obj.study.proposal
    elif type(obj) == Task:
        return obj.session.study.proposal
    elif type(obj) == Study:
        return obj.proposal
    else:
        print(type(obj))
        # Unknown/unsupported type
        return None


@register.inclusion_tag('base/stepper.html')
def stepper(obj, new=False, pre_assessment=False, pre_approved=False):
    """Generates a compare icon"""

    if proposal := _get_proposal_object(obj):
        return {
            'nav_items': proposal.available_urls()
        }
    elif new:
        proposal = Proposal()
        proposal.is_pre_approved = pre_approved
        proposal.is_pre_assessment = pre_assessment
        return {
            'nav_items': proposal.available_urls()
        }
    else:
        # Unknown/unsupported type, so we'll stop here
        return {}


@register.inclusion_tag('base/proposal_hero.html')
def proposal_hero(obj, new=False):
    """Generates a compare icon"""

    if proposal := _get_proposal_object(obj):
        return {
            'refnum': proposal.reference_number,
            'title': proposal.title,
        }
    elif new:
        return {
            'refnum': _('Nieuwe aanvraag')
        }
    else:
        # Unknown/unsupported type, so we'll stop here
        return {}


@register.inclusion_tag('base/form_buttons.html')
def form_buttons(obj, back=True):
    """Generates a compare icon"""

    if proposal := _get_proposal_object(obj):
        return {
            'proposal': proposal,
            'no_back': not back
        }
    else:
        # Unknown/unsupported type, so we'll stop here
        return {}
