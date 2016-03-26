# -*- encoding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import ugettext as _

from extra_views import UpdateWithInlinesView

from core.views import AllowErrorsMixin, LoginRequiredMixin, UserAllowedMixin, CreateView, UpdateView, success_url

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

    def get_context_data(self, **kwargs):
        context = super(StudyMixin, self).get_context_data(**kwargs)
        context['proposal'] = Proposal.objects.get(pk=self.kwargs['pk'])
        return context

    def get_form_kwargs(self):
        """Sets the Proposal as a form kwarg"""
        kwargs = super(StudyMixin, self).get_form_kwargs()
        kwargs['proposal'] = Proposal.objects.get(pk=self.kwargs['pk'])
        return kwargs

    def get_next_url(self):
        return reverse('proposals:study_consent', args=(self.object.pk,))

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
        next_url = 'proposals:session_end'
        pk = study.pk
        if study.has_observation:
            if hasattr(study, 'observation'):
                next_url = 'observations:update'
                pk = study.observation.pk
            else:
                next_url = 'observations:create'
        elif study.has_intervention:
            if hasattr(study, 'intervention'):
                next_url = 'interventions:update'
                pk = study.intervention.pk
            else:
                next_url = 'interventions:create'
        elif study.has_sessions:
            next_url = 'proposals:session_start'
        return reverse(next_url, args=(pk,))

    def get_back_url(self):
        return reverse('proposals:study_consent', args=(self.kwargs['pk'],))


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
        return reverse('proposals:submit', args=(self.object.proposal.pk,))

    def get_back_url(self):
        return reverse('proposals:session_end', args=(self.object.proposal.pk,))


################
# AJAX callbacks
################
@csrf_exempt
def check_necessity_required(request):
    """
    This call checks whether the necessity questions are required. They are required when:
    - The researcher requires a supervisor AND one of these cases applies:
        - A selected AgeGroup requires details.
        - Participants have been selected on certain traits.
        - Participants are legally incapable.
    """
    proposal = Proposal.objects.get(pk=request.POST.get('proposal_pk'))
    if not proposal.relation.needs_supervisor:
        result = False
    else:
        age_groups = map(int, request.POST.getlist('age_groups[]'))
        required_values = AgeGroup.objects.filter(needs_details=True).values_list('id', flat=True)
        result = bool(set(required_values).intersection(age_groups))
        result |= string_to_bool(request.POST.get('has_traits'))
        result |= string_to_bool(request.POST.get('legally_incapable'))

    return JsonResponse({'result': result})
