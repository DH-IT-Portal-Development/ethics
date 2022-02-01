from collections import Counter, defaultdict

from django.contrib.auth.models import Group
from django.db.models import QuerySet

from proposals.models import Proposal, Relation
from observations.models import Registration as ObsReg
from reviews.models import Review
from tasks.models import Registration as TasReg


#
# DATA FUNCTIONS
#


def get_qs_for_year(year: int) -> QuerySet:
    return Proposal.objects.filter(
        date_submitted__year=year,
        is_revision=False,
        status__gte=Proposal.DECISION_MADE,
    )


def get_qs_for_year_and_committee(year: int, committee: Group) -> QuerySet:
    return get_qs_for_year(year).filter(reviewing_committee=committee)


def get_review_qs_for_proposals(proposal_data: QuerySet) -> QuerySet:
    return Review.objects.filter(
        proposal__in=proposal_data,
    ).exclude(
        stage=Review.SUPERVISOR,
        date_end=None,
    )


def _get_review_qs_by_route(proposal_data: QuerySet, short_route: bool) -> \
        QuerySet:
    return get_review_qs_for_proposals(proposal_data).filter(
        short_route=short_route
    )


def get_qs_for_short_route_reviews(proposal_data: QuerySet) -> QuerySet:
    return _get_review_qs_by_route(proposal_data, True)


def get_qs_for_long_route_reviews(proposal_data: QuerySet) -> QuerySet:
    return _get_review_qs_by_route(proposal_data, False)


#
# STATISTICS FUNCTIONS
#


def get_total_submitted_proposals(data: QuerySet) -> int:
    return data.count()


def get_total_short_route_proposals(data: QuerySet) -> int:
    return get_qs_for_short_route_reviews(data).count()


def get_total_long_route_proposals(data: QuerySet) -> int:
    return get_qs_for_short_route_reviews(data).count()


def get_total_students(data: QuerySet) -> dict:
    relations = Relation.objects.filter(check_in_course=True)
    totals = defaultdict(int)
    for relation in relations:
        totals[relation.description_en] = data.filter(relation=relation).count()

    return totals


def get_total_turnaround_time(review_data: QuerySet) -> Counter:
    return Counter(
        [(x.date_end - x.date_start).days for x in review_data]
    )


def get_average_turnaround_time(review_data: QuerySet) -> float:
    total = review_data.count()

    # Protect against division by 0
    if total == 0:
        return 0

    # First calculate the delta in seconds and then divide it by 60 to get
    # hours and then by 24 to get a day representation in floats.
    # Sidenote; PYTHON WHY ARE MY ONLY OPTIONS MICROSECONDS, SECONDS AND DAYS
    # We don't sum the num of days, as some reviews are closed in less than a
    # day which would cause the calculation to ignore that review
    return sum(
        [(x.date_end - x.date_start).seconds / 60 / 24 for x in review_data]
    ) / total


#
# OUTPUT FUNCTIONS
#


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
