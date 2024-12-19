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
