from braces.views import UserFormKwargsMixin
from xhtml2pdf import pisa
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ImproperlyConfigured

from django.views.generic.base import TemplateResponseMixin
from django.http import HttpResponse
from django.template.loader import get_template

from .models import Proposal
from .forms import ProposalForm
from .utils.proposal_utils import pdf_link_callback

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

    #: Default filename for PDF downloads
    pdf_filename = "document.pdf"

    #: Determines if the user will see a "Save as" dialog
    pdf_save_as = True

    #: Optional custom content disposition
    content_disposition = None

    #: Additional params passed to :func:`render_to_pdf_response`
    pdf_kwargs = None

    #: Document type for the filename factory
    filename_factory = None

    def get_pdf_filename(self):
        """
        Returns :attr:`pdf_filename` value by default.

        If left blank the browser will display the PDF inline.
        Otherwise it will pop up the "Save as.." dialog.

        :rtype: :func:`str`
        """

        if self.filename_factory:
            return self.filename_factory(
                self.get_object(),
                self.pdf_filename,
            )

        return self.pdf_filename

    def get_content_disposition(self):
        """Should a view wish to set this disposition themselves
        dynamically, overwriting this method allows that."""

        # Check if a custom disposition is set
        if self.content_disposition:
            return self.content_disposition

        # Else, choose right disposition depending on save as
        cd = "attachment"
        if not self.pdf_save_as:
            cd = "inline"

        self.content_disposition = '{}; filename="{}"'.format(
            cd,
            self.get_pdf_filename())

        return self.content_disposition

    def get_pdf_response(self, context, dest=None, **response_kwargs):
        """Renders HTML from template and subsequently a pdf
        using xhtml2pdf"""

        if not dest:
            # Create a Django response object, and specify content_type as pdf
            # This is the default when using this view
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = self.get_content_disposition()
            dest = response

        # find the template and render it.
        template_names = self.get_template_names()

        if not (type(template_names) is tuple or list):
            raise ImproperlyConfigured(
                "get_template_names() should return a sequence of templates.",
            )
        if len(template_names) == 0:
            raise ImproperlyConfigured(
                "get_template_names() returned an empty list.",
            )
        template = get_template(template_names[0])
        html = template.render(context)

        # Create PDF with pisa object
        pisa_status = pisa.CreatePDF(
            html,
            dest=dest,
            link_callback=pdf_link_callback,
        )

        if pisa_status.err:
            return HttpResponse('We had some errors <pre>' + html + '</pre>')
        return dest

    def render_to_response(self, context, **response_kwargs):

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = self.get_content_disposition()

        return self.get_pdf_response(context, **response_kwargs, dest=response)
