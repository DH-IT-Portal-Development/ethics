from proposals.api.ddv_serializers import DDVProposalSerializer
from proposals.models import Proposal
from rest_framework import serializers


# We will be getting a list of reviews in this serializer (hence they belong in this module).
# Those reviews are shown as a proposal with additional review actions on top of them.
# We are importing the ProposalSerializer as it would cause a circular import in the normal review serializer.


class SecretaryApiSerializer(DDVProposalSerializer):
    class Meta:
        model = Proposal
        field = [
            "reference_number",
            "title",
            "type",
            "date_modified",
            "date_submitted",
            "detailed_state",
            "usernames",
            "supervisor_name",
            "my_secretary_actions",
        ]

    # own user and supervisor view do not need supervisor displayed but secretary needs to know.
    supervisor_name = serializers.SerializerMethodField()

    @staticmethod
    def get_supervisor_name(proposal: Proposal) -> str:
        if proposal.supervisor:
            return "Promotor/Begeleider" + proposal.supervisor.fullname
        return ""
