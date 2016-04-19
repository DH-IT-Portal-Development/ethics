def copy_observation_to_study(study, observation):
    setting = observation.setting.all()
    locations = observation.location_set.all()

    o = observation
    o.pk = None
    o.study = study
    o.save()

    o.setting = setting
    o.save()

    for location in locations:
        r = location.registrations.all()

        l = location
        l.pk = None
        l.observation = o
        l.save()

        l.registrations = r
        l.save()
