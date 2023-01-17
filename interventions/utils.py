from django.urls import reverse
from django.utils.translation import gettext as _

from main.utils import AvailableURL


def intervention_url(study, troublesome_urls):
    """
    Returns the available URLs for an Intervention
    """
    result = AvailableURL(title=_('Interventieonderzoek'), margin=2)
    if study.has_intervention:
        if hasattr(study, 'intervention'):
            result.url = reverse('interventions:update', args=(study.intervention.pk,))
        else:
            result.url = reverse('interventions:create', args=(study.pk,))
        result.has_errors = result.url in troublesome_urls
    return result


def copy_intervention_to_study(study, original_intervention):
    """
    Copies the given Intervention to the given Study
    """
    from interventions.models import Intervention

    i = Intervention.objects.get(pk=original_intervention.pk)
    i.pk = None
    i.version = 2  # Auto upgrade old versions
    i.study = study
    i.save()

    i.setting.set(original_intervention.setting.all())
    i.save()
