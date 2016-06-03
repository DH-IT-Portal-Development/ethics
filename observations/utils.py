from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from core.utils import AvailableURL


def observation_url(study):
    result = AvailableURL(title=_('Het observatieonderzoek'), margin=2)
    if study.has_observation:
        if hasattr(study, 'observation'):
            result.url = reverse('observations:update', args=(study.observation.pk,))
        else:
            result.url = reverse('observations:create', args=(study.pk,))
    return result


def copy_observation_to_study(study, observation):
    setting = observation.setting.all()
    registrations = observation.registrations.all()

    o = observation
    o.pk = None
    o.study = study
    o.save()

    o.setting = setting
    o.registrations = registrations.all()
    o.save()
