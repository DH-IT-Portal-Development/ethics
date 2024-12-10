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
