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

    def form_valid(self, form):
        """Creates or deletes Studies on save"""
        nr_studies = form.cleaned_data['studies_number']
        proposal = form.instance
        current = proposal.study_set.count() or 0

        # Create Studies
        for n in xrange(current, nr_studies):
            order = n + 1
            study = Study(proposal=proposal, order=order)
            study.save()

        # Delete Studies
        for n in xrange(nr_studies, current):
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
