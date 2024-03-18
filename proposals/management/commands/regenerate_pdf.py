from django.core.management.base import BaseCommand, CommandError
from proposals.models import Proposal


class Command(BaseCommand):
    help = "Regenerates the PDF for a Proposal"

    def add_arguments(self, parser):
        parser.add_argument(
            "reference_numbers",
            nargs="+",
            type=str,
            help="Space separated list of reference number for which PDFs \
            should be regenerated",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Force overwrite the existing PDF regardless of the \
            proposal's state. This applies to ALL reference numbers provided.",
        )

    def get_proposals(
        self,
    ):
        refnums = self.options["reference_numbers"]
        proposals = []
        for num in refnums:
            try:
                proposal = Proposal.objects.get(reference_number=num)
            except Proposal.DoesNotExist:
                raise CommandError(
                    f"""
                Proposal with reference number {num} could not be found.
                Aborting generation of all PDFs.
                """
                )
            proposals.append(proposal)
        return proposals

    def handle(self, *args, **options):
        self.options = options
        for proposal in self.get_proposals():
            print(f"Generating PDF for {proposal.reference_number}...", end=" ")
            proposal.generate_pdf(force_overwrite=options["force"])
            print("OK")
