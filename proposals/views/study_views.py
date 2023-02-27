# -*- encoding: utf-8 -*-

from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from main.views import AllowErrorsOnBackbuttonMixin, UpdateView, FormSetUpdateView
from studies.models import Documents, Study
from studies.forms import StudyConsentForm
from studies.utils import create_documents_for_study
from ..forms import StudyStartForm
from ..models import Proposal


class StudyStart(AllowErrorsOnBackbuttonMixin, UpdateView):
    model = Proposal
    form_class = StudyStartForm
    template_name = 'proposals/study_start.html'

    def get_form_kwargs(self):
        """Sets the Proposal as a form kwarg"""
        kwargs = super(StudyStart, self).get_form_kwargs()
        kwargs['proposal'] = self.object
        return kwargs

    def form_valid(self, form):
        """Creates or deletes Studies on save"""
        proposal = form.instance
        current = proposal.study_set.count() or 0
        if proposal.studies_similar:
            proposal.studies_number = 1

        # Create or update Studies
        for n in range(proposal.studies_number):
            order = n + 1
            s, _ = Study.objects.get_or_create(proposal=proposal, order=order)
            s.name = self.request.POST.get('study_name_' + str(order))
            s.save()

        # Delete Studies
        for n in range(proposal.studies_number, current):
            order = n + 1
            study = Study.objects.get(proposal=proposal, order=order)
            study.delete()

        return super(StudyStart, self).form_valid(form)

    def get_next_url(self):
        """Continue to the first Study"""
        proposal = self.object
        return reverse('studies:update', args=(proposal.first_study().pk,))

    def get_back_url(self):
        """Return to the Wmo overview"""
        return reverse('proposals:wmo_update', args=(self.object.wmo.pk,))


class StudyConsent(AllowErrorsOnBackbuttonMixin, FormSetUpdateView):
    """
    Allows the applicant to add informed consent to their Studies
    """
    success_message = _('Consent opgeslagen')
    template_name = 'proposals/study_consent.html'
    form = StudyConsentForm
    extra = 3
    
    def get(self, request, *args, **kwargs):
        """A bit of a hacky override to ensure only 2 extra document forms
        apart from the study document forms are presented"""

        proposal = Proposal.objects.get(pk=self.kwargs.get('pk'))

        self.extra = (len(proposal.study_set.all()) + self.extra) - \
            len(self.get_queryset().all())

        return super(StudyConsent, self).get(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        """Setting the progress on the context"""  # (??)
        context = super().get_context_data(*args, **kwargs)
        # The following is used by the progress bar
        proposal = Proposal.objects.get(pk=self.kwargs.get('pk'))
        context['proposal'] = proposal

        initial = []
        for i in range(self.extra):
            initial.append({'proposal': proposal.pk})
        context['formset'].initial_extra = initial

        # Tell the template if any studies need external forms
        studies = Study.objects.filter(proposal=proposal)
        context["external_permission"] = True in [
            s.needs_additional_external_forms() for s in studies
        ]
        return context

    def get_queryset(self):
        proposal = Proposal.objects.get(pk=self.kwargs.get('pk'))
        documents = Documents.objects.filter(proposal=proposal)

        if len(documents) == 0:
            for study in proposal.study_set.all():
                create_documents_for_study(study)

            return Documents.objects.filter(proposal=proposal)

        return documents


    def get_next_url(self):
        """
        If there is another Study in this Proposal, continue to that one.
        Otherwise, go to the data management view.
        """
        proposal = Proposal.objects.get(pk=self.kwargs.get('pk'))
        return reverse('proposals:data_management', args=(proposal.pk,))

    def get_back_url(self):
        """Return to the Study design view"""
        proposal = Proposal.objects.get(pk=self.kwargs.get('pk'))
        return reverse('studies:design_end', args=(proposal.last_study().pk,))

