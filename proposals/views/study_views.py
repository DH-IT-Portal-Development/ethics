# -*- encoding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import ugettext as _

from extra_views import UpdateWithInlinesView

from .base_views import CreateView, UpdateView, success_url
from ..mixins import AllowErrorsMixin, LoginRequiredMixin, UserAllowedMixin
from ..forms import StudyForm, StudyDesignForm, StudySurveyForm, SurveysInline
from ..models import Proposal, Study, AgeGroup
from ..utils import string_to_bool


#######################
# CRUD actions on Study
#######################
class StudyMixin(object):
    """Mixin for a Study, to use in both StudyCreate and StudyUpdate below"""
    model = Study
    form_class = StudyForm
    success_message = _('Studie opgeslagen')

    def get_next_url(self):
        return reverse('proposals:study_design', args=(self.object.pk,))

    def get_back_url(self):
        return reverse('proposals:wmo_update', args=(self.kwargs['pk'],))


class StudyCreate(StudyMixin, AllowErrorsMixin, CreateView):
    """Creates a Study from a StudyForm"""

    def form_valid(self, form):
        """Sets the Proposal on the Study before starting validation."""
        form.instance.proposal = Proposal.objects.get(pk=self.kwargs['pk'])
        return super(StudyCreate, self).form_valid(form)


class StudyUpdate(StudyMixin, AllowErrorsMixin, UpdateView):
    """Updates a Study from a StudyForm"""


class StudyDesign(AllowErrorsMixin, UpdateView):
    model = Study
    form_class = StudyDesignForm
    success_message = _('Studieontwerp opgeslagen')
    template_name = 'proposals/study_design.html'

    def get_next_url(self):
        study = self.object
        # TODO: send through based on selection
        return reverse('proposals:observation_create', args=(self.kwargs['pk'],))

    def get_back_url(self):
        return reverse('proposals:study_update', args=(self.kwargs['pk'],))


# NOTE: below view is non-standard, as it include inlines
# NOTE: no success message will be generated: https://github.com/AndrewIngram/django-extra-views/issues/59
class StudySurvey(LoginRequiredMixin, UserAllowedMixin, UpdateWithInlinesView):
    model = Study
    form_class = StudySurveyForm
    inlines = [SurveysInline]
    template_name = 'proposals/study_survey_form.html'

    def get_success_url(self):
        return success_url(self)

    def get_next_url(self):
        return reverse('proposals:consent', args=(self.object.proposal.id,))

    def get_back_url(self):
        return reverse('proposals:session_end', args=(self.object.proposal.id,))


################
# AJAX callbacks
################
@csrf_exempt
def check_necessity_required(request):
    """
    This call checks whether a certain value requires another input to be filled.
    """
    age_groups = map(int, request.POST.getlist('age_groups[]'))
    required_values = AgeGroup.objects.filter(needs_details=True).values_list('id', flat=True)
    result = bool(set(required_values).intersection(age_groups))
    result |= string_to_bool(request.POST.get('legally_incapable'))
    result |= string_to_bool(request.POST.get('has_traits'))

    return JsonResponse({'result': result})
