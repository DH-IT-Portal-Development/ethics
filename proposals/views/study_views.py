# -*- encoding: utf-8 -*-

from django.core.urlresolvers import reverse

from core.views import AllowErrorsMixin, UpdateView
from studies.models import Study
from ..forms import StudyStartForm
from ..models import Proposal


class StudyStart(AllowErrorsMixin, UpdateView):
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
        for n in xrange(proposal.studies_number):
            order = n + 1
            s, _ = Study.objects.get_or_create(proposal=proposal, order=order)
            s.name = self.request.POST['study_name_' + str(order)]
            s.save()

        # Delete Studies
        for n in xrange(proposal.studies_number, current):
            order = n + 1
            study = Study.objects.get(proposal=proposal, order=order)
            study.delete()

        return super(StudyStart, self).form_valid(form)

    def get_next_url(self):
        """Continue to the first Study"""
        proposal = self.object
        return reverse('studies:update', args=(proposal.first_study().pk,))

    def get_back_url(self):
        return reverse('proposals:wmo_update', args=(self.object.wmo.pk,))
