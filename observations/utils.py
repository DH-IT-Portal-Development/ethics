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
