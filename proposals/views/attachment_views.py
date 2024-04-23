from django.views import generic

from proposals.models import Proposal
from attachments.kinds import ATTACHMENTS
from attachments.utils import AttachmentContainer, ProposalAttachments
from attachments.models import Attachment

class AttachmentsView(generic.DetailView):

    model = Proposal
    template_name = "proposals/proposal_attachments.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        proposal = self.get_object()
        proposal_attachments = ProposalAttachments(proposal)
        context.update({
            "attachment_kinds": [a(proposal) for a in ATTACHMENTS],
            "proposal_attachments": proposal_attachments,
        })
        attachment = Attachment()
        context.update(
            {
                "my_attachment": AttachmentContainer(attachment),
            }
        )
        return context
