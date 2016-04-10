def copy_intervention_to_study(study, intervention):
    i = intervention
    i.pk = None
    i.study = study
    i.save()
