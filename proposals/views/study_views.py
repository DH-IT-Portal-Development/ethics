# -*- encoding: utf-8 -*-

from django.core.urlresolvers import reverse

from braces.views import LoginRequiredMixin
from extra_views import UpdateWithInlinesView

from core.views import UserAllowedMixin, success_url
from studies.models import Study

from ..forms import StudyStartForm, StudiesInline
from ..models import Proposal


class StudyStart(LoginRequiredMixin, UserAllowedMixin, UpdateWithInlinesView):
    model = Proposal
    form_class = StudyStartForm
    inlines = [StudiesInline]
    template_name = 'proposals/study_start.html'

    def forms_valid(self, form, inlines):
        """
        - If the studies_similar is set, set studies_number to 1 and remove superfluous Studies
        """
        if form.instance.studies_similar:
            form.instance.studies_number = 1
            inlines = []
            Study.objects.filter(proposal=form.instance,
                                 order__gt=form.instance.studies_number).delete()

        return super(StudyStart, self).forms_valid(form, inlines)

    def get_success_url(self):
        return success_url(self)

    def get_next_url(self):
        """Continue to the first Study"""
        return reverse('studies:update', args=(self.object.first_study().pk,))

    def get_back_url(self):
        """Continue to WMO"""
        return reverse('proposals:wmo_update', args=(self.object.wmo.pk,))
