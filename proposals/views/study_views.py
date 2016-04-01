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
        """Deletes superfluous Studies on save"""
        nr_studies = form.cleaned_data['studies_number']
        proposal = form.instance
        current = proposal.session_set.count() or 0

        for n in xrange(nr_studies, current):
            order = n + 1
            study = Study.objects.get(proposal=proposal, order=order)
            study.delete()

        return super(StudyStart, self).form_valid(form)

    def get_next_url(self):
        """Continue to the first Study, or create a new one."""
        proposal = self.object
        if proposal.first_study():
            return reverse('studies:update', args=(proposal.first_study().pk,))
        else:
            return reverse('studies:create', args=(proposal.pk,))

    def get_back_url(self):
        return reverse('proposals:wmo_update', args=(self.object.wmo.pk,))
