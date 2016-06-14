from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from core.utils import AvailableURL


def intervention_url(study):
    """
    Returns the available URLs for an Intervention
    """
    result = AvailableURL(title=_('Het interventieonderzoek'), margin=2)
    if study.has_intervention:
        if hasattr(study, 'intervention'):
            result.url = reverse('interventions:update', args=(study.intervention.pk,))
        else:
            result.url = reverse('interventions:create', args=(study.pk,))
    return result


def copy_intervention_to_study(study, intervention):
    """
    Copies the given Intervention to the given Study
    """
    setting = intervention.setting.all()

    i = intervention
    i.pk = None
    i.study = study
    i.save()

    i.setting = setting
    i.save()
