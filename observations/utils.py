from django.urls import reverse
from django.utils.translation import gettext as _

from main.utils import AvailableURL


def observation_url(study, troublesome_urls):
    result = AvailableURL(title=_('Observatieonderzoek'), margin=2)
    if study.has_observation:
        if hasattr(study, 'observation'):
            result.url = reverse('observations:update', args=(study.observation.pk,))
        else:
            result.url = reverse('observations:create', args=(study.pk,))
        result.has_errors = result.url in troublesome_urls
    return result


def copy_observation_to_study(study, original_observation):
    from observations.models import Observation

    o = Observation.objects.get(pk=original_observation.pk)
    o.pk = None
    o.version = 2
    o.study = study
    o.save()

    o.setting.set(original_observation.setting.all())
    o.registrations.set(original_observation.registrations.all())
    o.save()
