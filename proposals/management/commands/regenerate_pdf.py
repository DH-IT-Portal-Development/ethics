from django.core.management.base import BaseCommand, CommandError
from proposals.models import Proposal

class Command(BaseCommand):
    help = 'Regenerates the PDF for a Proposal'

    def add_arguments(self, parser):
        parser.add_argument('reference_numbers', nargs='+', type=str)

    def get_proposals(self, ):
        refnums = self.options["reference_numbers"]
        proposals = []
        for num in refnums:
            try:
                proposal = Proposal.objects.get(reference_number=num)
            except Proposal.DoesNotExist:
                raise CommandError(f"""
                Proposal with reference number {num} could not be found.
                Aborting generation of all PDFs.
                """)
            proposals.append(proposal)
        return proposals

    def handle(self, *args, **options):
        for proposal in self.get_proposals():
            print(f"Generating PDF for {proposal.reference_number}...", end=" ")
            proposal.generate_pdf()
            print("OK")
