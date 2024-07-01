from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command

import os, csv

from proposals.models import Proposal

class Command(BaseCommand):
    help = "Outputs some csv files with stats"

    headers = [
        "Kamer",
        "Referentienummer",
        "Instituut",
        "Typen onderzoek",
        "Typen registratie",
        "Indiener",
        "Soort indiener",
        "Eindverantwoordelijke",
        "Ingediend op",
        "Route",
        "Beslissing",
        "Besloten op",
        "Amendement?",
    ]

    def add_arguments(self, parser):
        parser.add_argument("year", type=int)

    def handle(self, *args, **kwargs):
        print("Getting stats")
        year = kwargs["year"]
        qs_for_year = Proposal.objects.filter(
            date_submitted__year=year,
        ).order_by("reference_number")
        querysets = [
            (
                "both",
                qs_for_year,
            )
        ]
        for name, qs in querysets:
            self.write_for_qs(qs, name)
        print("Done!")

    def write_for_qs(self, qs, name):
        p = qs.first()
        headers = Row(p).get_row_dict().keys()
        with open(name+ ".csv", "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            for proposal in qs:
                writer.writerow(
                    Row(proposal).as_dict(),
                )

class Row:

    def __init__(self, proposal):
        self.proposal = proposal
        self.review = proposal.latest_review()

    @property
    def is_amendment(self):
        if not (
            self.proposal.parent and
            self.proposal.is_revision
        ):
            return False
        if self.proposal.parent.status_review:
            # A positive status_review means it was previously accepted
            # and a subsequent revision must be an amendment
            return True
        return False

    def get_reviewing_chamber(self):
        institute = self.proposal.institution
        return institute.reviewing_chamber.name

    def get_route(self):
        r = self.review
        if r.short_route is True:
            return "Korte route"
        elif r.short_route is False:
            return "Lange route"
        else:
            return "Onbekend"

    def as_dict(self):
        row_dict = self.get_row_dict()
        for k, v in row_dict.items():
            if callable(v):
                row_dict[k] = v()
        return row_dict

    def get_continuation(self,):
        return self.review.get_continuation_display()

    def get_decision_date(self,):
        return self.proposal.date_reviewed

    def get_registrations(self,):
        regs = set()
        for s in self.proposal.study_set.all():
            if s.has_observation:
                for reg in s.observation.registrations.all():
                    regs.add(reg)
            for session in s.session_set.all():
                for task in session.task_set.all():
                    for reg in task.registrations.all():
                        regs.add(reg)
        out = sorted(
            [reg for reg in regs],
            key=lambda reg: reg.pk,
        )
        out = [reg.description for reg in out]

    def get_study_types(self,):
        types = set()
        p = self.proposal
        for s in self.proposal.study_set.all():
            if s.has_intervention:
                types.add("Interventie")
            if s.has_observation:
                types.add("Observatie")
            if s.has_sessions:
                types.add("Taakonderzoek en interviews")
        return ", ".join(types)

    def get_row_dict(self,):
        p = self.proposal
        return {
            "Kamer": self.get_reviewing_chamber,
            "Referentienummer": p.reference_number,
            "Instituut": p.institution.description,
            "Typen onderzoek": self.get_study_types,
            "Typen registratie": self.get_registrations,
            "Indiener": p.created_by,
            "Soort indiener": p.relation.description,
            "Eindverantwoordelijke": p.supervisor,
            "Opgestuurd naar eindverantwoordelijke": (
                p.date_submitted_supervisor
            ),
            "Ingediend op": p.date_submitted,
            "Route": self.get_route,
            "Beslissing": self.get_continuation,
            "Besloten op": self.get_decision_date,
            "Amendement?": self.get_amendment,
        }

    def get_amendment(self, row_dict):
        amendment = "Nee"
        if self.is_amendment:
            amendment = "Ja"
        row_dict["Amendement?"] = amendment
