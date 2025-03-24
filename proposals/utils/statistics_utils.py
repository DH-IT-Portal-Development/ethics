from collections import Counter, defaultdict
import statistics

from django.contrib.auth.models import Group
from django.db.models import QuerySet

from proposals.models import Proposal, Relation
from studies.models import Registration
from reviews.models import Review


#
# DATA FUNCTIONS
#


def get_qs_for_year(year: int) -> QuerySet:
    """Returns a QuerySet for all *original* proposals in the supplied year
    that have been concluded. Note that 'original' means that revision
    proposals are excluded. (As requested by the secretary).

    :param year: int, specifies which year should be used to select proposals
    :return: a selection of Proposals submitted in the given year
    :rtype: QuerySet[Proposal]
    """
    return Proposal.objects.filter(
        date_submitted__year=year,
        is_revision=False,
        status__gte=Proposal.Statuses.DECISION_MADE,
    )


def get_qs_for_year_and_committee(year: int, committee: Group) -> QuerySet:
    """Returns a QuerySet for all *original* concluded proposals in the
    supplied year that were processed by the supplied committee.
    Note that 'original' means that revision proposals are excluded. (As
    requested by the secretary).

    :param year: int, specifies which year should be used to select proposals
    :param committee: Group, the Group that should be used to filter
    :return: a selection of Proposals meeting the given criteria
    :rtype: QuerySet[Proposal]
    """
    return get_qs_for_year(year).filter(reviewing_committee=committee)


def get_review_qs_for_proposals(proposal_data: QuerySet) -> QuerySet:
    """Returns a queryset containing all non-supervisor Review objects for
    the given QuerySet of proposals.

    :param proposal_data: QuerySet[Proposal], A QS of proposals to find
    Review's for
    :return: all Reviews for the given proposals
    :rtype: QuerySet[Review]
    """
    return Review.objects.filter(
        proposal__in=proposal_data,
    ).exclude(
        stage=Review.Stages.SUPERVISOR,
        date_end=None,
    )


def _get_review_qs_by_route(proposal_data: QuerySet, short_route: bool) -> QuerySet:
    """Returns all Reviews for the given proposals and taken route"""
    return get_review_qs_for_proposals(proposal_data).filter(short_route=short_route)


def get_qs_for_short_route_reviews(proposal_data: QuerySet) -> QuerySet:
    """Returns a queryset containing all non-supervisor Review objects that
    have taken the short review route for the given QuerySet of proposals.

    :param proposal_data: QuerySet[Proposal], A QS of proposals to find
    Review's for
    :return: all Reviews for the given proposals
    :rtype: QuerySet[Review]
    """
    return _get_review_qs_by_route(proposal_data, True)


def get_qs_for_long_route_reviews(proposal_data: QuerySet) -> QuerySet:
    """Returns a queryset containing all non-supervisor Review objects that
    have taken the long review route for the given QuerySet of proposals.

    :param proposal_data: QuerySet[Proposal], A QS of proposals to find
    Review's for
    :return: all Reviews for the given proposals
    :rtype: QuerySet[Review]
    """
    return _get_review_qs_by_route(proposal_data, False)


#
# STATISTICS FUNCTIONS
#


def get_total_submitted_proposals(data: QuerySet) -> int:
    """'Calculates' the total amount of proposals in the data

    :param data: QuerySet[Proposal], the proposals to calculate this
    statistic for
    :return: the num of proposals in the given QuerySet
    :rtype: int
    """
    return data.count()


def get_total_short_route_proposals(data: QuerySet) -> int:
    """Calculates the total amount of proposals in the data that were reviewed
    using the short route.

    :param data: QuerySet[Proposal], the proposals to calculate this
    statistic for
    :return: the num of short route proposals in the given QuerySet
    :rtype: int
    """
    return get_qs_for_short_route_reviews(data).count()


def get_total_long_route_proposals(data: QuerySet) -> int:
    """Calculates the total amount of proposals in the data that were reviewed
    using the long route.

    :param data: QuerySet[Proposal], the proposals to calculate this
    statistic for
    :return: the num of long route proposals in the given QuerySet
    :rtype: int
    """
    return get_qs_for_long_route_reviews(data).count()


def get_total_students(data: QuerySet) -> dict:
    """Calculates a dict of all Relations that are deemed to be students,
    and a corresponding number of occurrences in the supplied Proposals.

    :param data: QuerySet[Proposal], the proposals to calculate this
    statistic for
    :return: A dict of (relation, count) pairs
    :rtype: dict
    """
    relations = Relation.objects.filter(check_in_course=True)
    totals = defaultdict(int)
    for relation in relations:
        totals[relation.description_en] = data.filter(relation=relation).count()

    return totals


def get_total_turnaround_time(review_data: QuerySet) -> Counter:
    """Calculates the amount of days it took to conclude a review, and puts
    them in a counter, in which the left-hand side represents the number of
    days and the right-hand side represents the number of reviews concluded
    in that amount of days

    :param review_data: QuerySet[Review], the reviews to calculate this
    statistic for
    :return: A Counter of (days, count) pairs
    :rtype: Counter
    """
    return Counter([(x.date_end - x.date_start).days for x in review_data])


def get_average_turnaround_time(review_data: QuerySet) -> float:
    """Calculates the average time it took to conclude all reviews in the
    given dataset

    :param review_data: QuerySet[Review], the reviews to calculate this
    statistic for
    :return: the average turnaround time on a review, expressed in days (
    using a float to represent partial days)
    :rtype: float
    """
    return statistics.mean([(x.date_end - x.date_start).days for x in review_data])


#
# OUTPUT FUNCTIONS
#


def get_registrations_for_proposal(proposal: Proposal) -> dict:
    """Looks at all studies, and returns a dict of studies and the
    registration kinds of said studies.

    :param proposal: Proposal, the proposal to get the registrations for
    :return: all registrations, properly ordered and coded
    :rtype: dict[int, list[str]]
    """
    registrations = defaultdict(list)

    for study in proposal.study_set.all():
        for registration in study.registrations.all():
            if registration in Registration.objects.filter(needs_details=True):
                registrations[study.order].append(f"{registration.description}: {study.registration_details}")
            else:
                registrations[study.order].append(f"{registration.description}")

    return registrations


def get_studytypes_for_proposal(proposal: Proposal) -> dict:
    """Looks at all studies, and records per study if they have intervention,
    observation and/or task research.

    :param proposal: Proposal, the proposal to get the research types for
    :return: all studies with the research types they use
    :rtype: dict[int, list[str]]
    """
    study_types = defaultdict(list)

    for study in proposal.study_set.all():
        if study.get_intervention():
            study_types[study.order].append("intervention")
        if study.get_observation():
            study_types[study.order].append("observation")
        if study.get_sessions():
            study_types[study.order].append("task")

    return study_types
