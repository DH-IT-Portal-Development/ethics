from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand
from django.conf import settings
from django.views.i18n import set_language

from proposals.utils.statistics_utils import (
    get_average_turnaround_time,
    get_qs_for_long_route_reviews,
    get_qs_for_short_route_reviews,
    get_qs_for_year,
    get_qs_for_year_and_committee,
    get_review_qs_for_proposals,
    get_total_long_route_proposals,
    get_total_short_route_proposals,
    get_total_students,
    get_total_submitted_proposals,
)


class Command(BaseCommand):
    help = "Calculate statistics for a given year"

    def add_arguments(self, parser):
        parser.add_argument("year", type=int)

    def handle(self, *args, **options):
        AK = Group.objects.get(name=settings.GROUP_GENERAL_CHAMBER)
        LK = Group.objects.get(name=settings.GROUP_LINGUISTICS_CHAMBER)

        datasets = {
            "Total": get_qs_for_year(options["year"]),
            "AK": get_qs_for_year_and_committee(options["year"], AK),
            "LK": get_qs_for_year_and_committee(options["year"], LK),
        }

        for name, dataset in datasets.items():
            print(name)

            print("Total submitted:", get_total_submitted_proposals(dataset))
            print("Total short route:", get_total_short_route_proposals(dataset))
            print("Total long route:", get_total_long_route_proposals(dataset))

            print()
            print("Total per relation:")
            for relation, count in get_total_students(dataset).items():
                print(count, relation)

            print()
            print("Turnaround times:")
            print(
                "Short route",
                get_average_turnaround_time(get_qs_for_short_route_reviews(dataset)),
                "days",
            )
            print(
                "Long route",
                get_average_turnaround_time(get_qs_for_long_route_reviews(dataset)),
                "days",
            )

            print()
