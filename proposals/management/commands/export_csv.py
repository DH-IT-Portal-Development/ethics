import csv

from django.core.management.base import BaseCommand

from proposals.utils.statistics_utils import get_qs_for_year, \
    get_registrations_for_proposal, get_studytypes_for_proposal


class Command(BaseCommand):
    help = 'Exports reviewed Proposals'

    def add_arguments(self, parser):
        parser.add_argument('year', type=int)

    def handle(self, *args, **options):

        with open('output.csv', 'w') as csvfile:
            csv_writer = csv.writer(
                csvfile,
                delimiter=',',
                quotechar='"',
                quoting=csv.QUOTE_MINIMAL
            )

            header = [
                'title',
                'reference_number',
                'reviewing committee',
                'type(s) of research',
                'registration type(s)',
                'applicant',
                'applicant type',
                'supervisor',
                'submitted on',
                'route',
                'conclusion',
                'concluded on'
            ]
            csv_writer.writerow(header)

            rows = []
            for proposal in get_qs_for_year(options['year']):
                study_types = get_studytypes_for_proposal(proposal)
                registrations = get_registrations_for_proposal(proposal)

                row = [
                    proposal.title,
                    proposal.reference_number,
                    proposal.reviewing_committee.name,
                    dict_to_string(study_types),
                    dict_to_string(registrations),
                    proposal.created_by.get_full_name(),
                    proposal.relation.description,
                    proposal.accountable_user().get_full_name(),
                    proposal.date_submitted.date().isoformat(),
                ]

                review = proposal.latest_review()
                row.extend(
                    [
                        'short' if review.short_route else 'long',
                        review.get_continuation_display(),
                        review.date_end.date().isoformat()
                    ]
                )

                rows.append(row)

            csv_writer.writerows(rows)


def dict_to_string(dict_):
    result = []
    for k, v in dict_.items():
        result.append(str(k) + ' - ' + ', '.join(v))
    return result[0].split(' - ')[1] if len(result) == 1 else '; '.join(result)
