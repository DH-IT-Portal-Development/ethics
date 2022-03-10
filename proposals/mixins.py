from braces.views import UserFormKwargsMixin
from .models import Proposal
from .forms import ProposalForm
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from django.views.generic.base import TemplateResponseMixin
from xhtml2pdf import pisa
from django.http import HttpResponse
from django.template.loader import get_template


class ProposalMixin(UserFormKwargsMixin):
    model = Proposal
    form_class = ProposalForm
    success_message = _('Aanvraag %(title)s bewerkt')

    def get_next_url(self):
        """If the Proposal has a Wmo model attached, go to update, else, go to create"""
        proposal = self.object
        if hasattr(proposal, 'wmo'):
            return reverse('proposals:wmo_update', args=(proposal.pk,))
        else:
            return reverse('proposals:wmo_create', args=(proposal.pk,))


class ProposalContextMixin:

    def current_user_is_supervisor(self):
        return self.object.supervisor == self.request.user

    def get_context_data(self, **kwargs):
        context = super(ProposalContextMixin, self).get_context_data(**kwargs)
        context['is_supervisor'] = self.current_user_is_supervisor()
        context['is_practice'] = self.object.is_practice()
        return context


class PDFTemplateResponseMixin(TemplateResponseMixin):
    """
    A mixin class that implements PDF rendering and Django response construction.
    """

    #: Optional name of the PDF file for download. Leave blank for display in browser.
    pdf_filename = None

    #: Additional params passed to :func:`render_to_pdf_response`
    pdf_kwargs = None

    def get_pdf_filename(self):
        """
        Returns :attr:`pdf_filename` value by default.

        If left blank the browser will display the PDF inline.
        Otherwise it will pop up the "Save as.." dialog.

        :rtype: :func:`str`
        """
        return self.pdf_filename

    def get_pdf_response(self, context, dest=None, **response_kwargs):
        """Renders HTML from template and subsequently a pdf
        using xhtml2pdf"""

        if not dest:
            # Create a Django response object, and specify content_type as pdf
            # This is the default when using this view
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="{}"'.format(
                self.get_pdf_filename)
            dest = response

        # find the template and render it.
        template = get_template(self.template_name)
        html = template.render(context)

        # Create PDF with pisa object
        pisa_status = pisa.CreatePDF(
            html, dest=dest, )

        if pisa_status.err:
            return HttpResponse('We had some errors <pre>' + html + '</pre>')
        return response

    def render_to_response(self, context, **response_kwargs):

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="{}"'.format(
            self.get_pdf_filename())

        return self.get_pdf_response(context, **response_kwargs)
