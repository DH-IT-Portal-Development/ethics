def copy_observation_to_study(study, observation):
    locations = observation.location_set.all()

    o = observation
    o.pk = None
    o.study = study
    o.save()

    for location in locations:
        r = location.registrations.all()

        l = location
        l.pk = None
        l.observation = o
        l.save()

        l.registrations = r
        l.save()
