from collections import defaultdict

from django.contrib.auth.models import Group
from django.db.models import QuerySet

from proposals.models import Proposal
from observations.models import Registration as ObsReg
from tasks.models import Registration as TasReg


def get_qs_for_year(year: int) -> QuerySet:
    return Proposal.objects.filter(
        date_submitted__year=year,
        is_revision=False,
        status__gte=Proposal.DECISION_MADE,
    )


def get_qs_for_year_and_committee(year: int, committee: Group) -> QuerySet:
    return get_qs_for_year(year).filter(reviewing_committee=committee)


def get_registrations_for_proposal(proposal: Proposal) -> dict:
    registrations = defaultdict(list)

    for study in proposal.study_set.all():
        if study.has_observation:
            for registration in study.observation.registrations.all():
                if registration in ObsReg.objects.filter(needs_details=True):
                    registrations[study.order].append(
                        'obs: {}: {}'.format(registration.description,
                                             study.observation.registrations_details))
                else:
                    registrations[study.order].append(
                        'obs: {}'.format(registration.description))
        if study.has_sessions:
            for session in study.session_set.all():
                for task in session.task_set.all():
                    for registration in task.registrations.all():
                        if registration in TasReg.objects.filter(
                                needs_details=True):
                            registrations[study.order].append(
                                's{}t{}: {}: {}'.format(
                                    session.order,
                                    task.order,
                                    registration.description,
                                    task.registrations_details)
                            )
                        else:
                            registrations[study.order].append(
                                's{}t{}: {}'.format(
                                    session.order,
                                    task.order,
                                    registration.description)
                            )

    return registrations


def get_studytypes_for_proposal(proposal: Proposal) -> dict:
    study_types = defaultdict(list)

    for study in proposal.study_set.all():
        if study.has_intervention:
            study_types[study.order].append('intervention')
        if study.has_observation:
            study_types[study.order].append('observation')
        if study.has_sessions:
            study_types[study.order].append('task')

    return study_types

