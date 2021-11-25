import codecs
import csv
import io
from collections import defaultdict

from django.core.management.base import BaseCommand

from proposals.models import Proposal
from reviews.models import Review
from observations.models import Registration as ObsReg
from tasks.models import Registration as TasReg


class Command(BaseCommand):
    help = 'Exports reviewed Proposals'

    def handle(self, *args, **options):

        with open('output.csv', 'wb') as csvfile:
            csvfile.write(u'\uFEFF'.encode('utf-8'))  # the UTF-8 BOM to hint Excel we are using that...
            csv_writer = UnicodeWriter(csvfile, delimiter=';')

            header = ['titel aanvraag', 'type(s) aanvraag', 'registratie', 'indiener', 'eindverantwoordelijke', 'ingediend op', 'route', 'afhandeling', 'afgehandeld op']
            csv_writer.writerow(header)

            rows = []
            for proposal in Proposal.objects.all():
                if proposal.status >= Proposal.DECISION_MADE:

                    study_types = defaultdict(list)
                    registrations = defaultdict(list)
                    for study in proposal.study_set.all():
                        if study.has_intervention:
                            study_types[study.order].append('interventie')
                        if study.has_observation:
                            study_types[study.order].append('observatie')
                            for registration in study.observation.registrations.all():
                                if registration in ObsReg.objects.filter(needs_details=True):
                                    registrations[study.order].append('obs: {}: {}'.format(registration.description, study.observation.registrations_details))
                                else:
                                    registrations[study.order].append('obs: {}'.format(registration.description))
                        if study.has_sessions:
                            study_types[study.order].append('taak')
                            for session in study.session_set.all():
                                for task in session.task_set.all():
                                    for registration in task.registrations.all():
                                        if registration in TasReg.objects.filter(needs_details=True):
                                            registrations[study.order].append('s{}t{}: {}: {}'.format(session.order, task.order, registration.description, task.registrations_details))
                                        else:
                                            registrations[study.order].append('s{}t{}: {}'.format(session.order, task.order, registration.description))

                    row = [proposal.title,
                           dict_to_string(study_types),
                           dict_to_string(registrations),
                           proposal.created_by.get_full_name(),
                           proposal.accountable_user().get_full_name(),
                           proposal.date_submitted.date().isoformat()]

                    reviews = Review.objects.filter(proposal=proposal, stage=Review.CLOSED)
                    if reviews.count() > 1:
                        print('Meer dan 1 Review voor Proposal {}'.format(proposal.reference_number))
                    for review in reviews:
                        row.extend(['kort' if review.short_route else 'lang',
                                    review.get_continuation_display(),
                                    review.date_end.date().isoformat()])

                    rows.append(row)

            csv_writer.writerows(rows)


def dict_to_string(dict_):
    result = []
    for k, v in dict_.items():
        result.append(str(k) + ' - ' + ', '.join(v))
    return result[0].split(' - ')[1] if len(result) == 1 else '; '.join(result)


class UnicodeWriter(object):
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    Copied from https://docs.python.org/2/library/csv.html#examples
    """

    def __init__(self, f, dialect=csv.excel, encoding='utf-8', **kwds):
        # Redirect output to a queue
        self.queue = io.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode('utf-8') for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode('utf-8')
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)
