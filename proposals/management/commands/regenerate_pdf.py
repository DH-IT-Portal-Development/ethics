from django.core.management.base import BaseCommand, CommandError

from proposals.models import Proposal
from proposals.utils import generate_pdf


class Command(BaseCommand):
    help = 'Regenerates the PDF for a Proposal'

    def add_arguments(self, parser):
        parser.add_argument('reference_numbers', nargs='+', type=str)

    def handle(self, *args, **options):
        for reference_number in options['reference_numbers']:
            try:
                proposal = Proposal.objects.get(reference_number=reference_number)
                if proposal.is_pre_assessment:
                    generate_pdf(proposal, 'proposals/proposal_pdf_pre_assessment.html')
                else:
                    generate_pdf(proposal, 'proposals/proposal_pdf.html')
            except Proposal.DoesNotExist:
                raise CommandError('Proposal with reference number {} not found'.format(reference_number))
