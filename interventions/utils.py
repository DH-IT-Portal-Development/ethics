def copy_intervention_to_study(study, intervention):
    setting = intervention.setting.all()

    i = intervention
    i.pk = None
    i.study = study
    i.save()

    i.setting = setting
    i.save()
