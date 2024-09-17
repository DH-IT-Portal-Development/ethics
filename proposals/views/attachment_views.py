from django.views import generic

class ProposalAttachments(generic.TemplateView):

    template_name = "proposals/attachments/proposal_attachments.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        return context
