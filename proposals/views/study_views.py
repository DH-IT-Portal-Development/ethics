# -*- encoding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.http import JsonResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt

from extra_views import CreateWithInlinesView, UpdateWithInlinesView

from .base_views import success_url
from ..mixins import LoginRequiredMixin, UserAllowedMixin
from ..forms import StudyForm, SurveysInline
from ..models import Proposal, Study, AgeGroup
from ..utils import string_to_bool


#######################
# CRUD actions on Study
#######################
class StudyMixin(object):
    """Mixin for a Study, to use in both StudyCreate and StudyUpdate below"""
    model = Study
    form_class = StudyForm
    inlines = [SurveysInline]

    def get_success_url(self):
        return success_url(self)

    def get_next_url(self):
        return reverse('proposals:session_start', args=(self.object.proposal.id,))

    def get_back_url(self):
        return reverse('proposals:wmo_update', args=(self.kwargs['pk'],))


# NOTE: below two views are non-standard, as they include inlines
# NOTE: no success message will be generated: https://github.com/AndrewIngram/django-extra-views/issues/59
class StudyCreate(StudyMixin, LoginRequiredMixin, CreateWithInlinesView):
    """Creates a Study from a StudyForm, with Surveys inlined."""

    def forms_valid(self, form, inlines):
        """Sets the Proposal on the Study before starting validation."""
        form.instance.proposal = Proposal.objects.get(pk=self.kwargs['pk'])
        return super(StudyCreate, self).forms_valid(form, inlines)

    def forms_invalid(self, form, inlines):
        """On back button, allow form to have errors."""
        if 'save_back' in self.request.POST:
            return HttpResponseRedirect(self.get_back_url())
        else:
            return super(StudyCreate, self).forms_invalid(form, inlines)


class StudyUpdate(StudyMixin, LoginRequiredMixin, UserAllowedMixin, UpdateWithInlinesView):
    """Updates a Study from a StudyForm, with Surveys inlined."""


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
    result |= string_to_bool(request.POST.get('has_traits'))

    return JsonResponse({'result': result})
