from proposals.api.ddv_views import ProposalApiView
from proposals.models import Proposal
from reviews.api.ddv_serializers import SecretaryApiSerializer


class MySecretaryApiView(ProposalApiView):
    serializer_class = SecretaryApiSerializer

    def get_queryset(self):
        """Returns all Proposals of current committee"""
        return Proposal.objects.filter(committee=self.request.committee)
