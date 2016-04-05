# -*- encoding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import ugettext as _

from core.views import AllowErrorsMixin, CreateView, UpdateView
from core.utils import string_to_bool
from proposals.models import Proposal

from ..forms import StudyForm, StudyDesignForm, StudyConsentForm
from ..models import Study
from ..utils import check_necessity_required, get_study_progress


#######################
# CRUD actions on Study
#######################
class StudyMixin(object):
    """Mixin for a Study, to use in both StudyCreate and StudyUpdate below"""
    model = Study
    form_class = StudyForm
    success_message = _('Studie opgeslagen')

    def get_next_url(self):
        return reverse('studies:design', args=(self.object.pk,))


class StudyCreate(StudyMixin, AllowErrorsMixin, CreateView):
    """Creates a Study from a StudyForm"""

    def get_context_data(self, **kwargs):
        """Setting the Proposal and order on the context"""
        context = super(StudyMixin, self).get_context_data(**kwargs)
        proposal = Proposal.objects.get(pk=self.kwargs['pk'])
        context['proposal'] = proposal
        context['order'] = proposal.study_set.count() + 1
        context['progress'] = get_study_progress(self.object)
        return context

    def get_form_kwargs(self):
        """Sets the Proposal as a form kwarg"""
        kwargs = super(StudyMixin, self).get_form_kwargs()
        kwargs['proposal'] = Proposal.objects.get(pk=self.kwargs['pk'])
        return kwargs

    def form_valid(self, form):
        """Sets the Proposal and the order field on the Study after the form has been validated."""
        proposal = Proposal.objects.get(pk=self.kwargs['pk'])
        form.instance.proposal = proposal
        form.instance.order = proposal.study_set.count() + 1
        return super(StudyCreate, self).form_valid(form)

    def get_back_url(self):
        # TODO: this is not correct, depends on the order
        return reverse('proposals:study_start', args=(self.kwargs['pk'],))


class StudyUpdate(StudyMixin, AllowErrorsMixin, UpdateView):
    """Updates a Study from a StudyForm"""

    def get_context_data(self, **kwargs):
        """Setting the Proposal and order on the context"""
        context = super(StudyMixin, self).get_context_data(**kwargs)
        context['proposal'] = self.object.proposal
        context['order'] = self.object.order
        context['progress'] = get_study_progress(self.object)
        return context

    def get_form_kwargs(self):
        """Sets the Proposal as a form kwarg"""
        kwargs = super(StudyMixin, self).get_form_kwargs()
        kwargs['proposal'] = self.object.proposal
        return kwargs

    def get_back_url(self):
        # TODO: this is not correct, depends on the order
        return reverse('proposals:study_start', args=(self.object.proposal.pk,))


###############
# Other actions
###############
class StudyDesign(AllowErrorsMixin, UpdateView):
    model = Study
    form_class = StudyDesignForm
    success_message = _('Studieontwerp opgeslagen')
    template_name = 'studies/study_design.html'

    def get_next_url(self):
        study = self.object
        next_url = 'studies:session_end'
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
            next_url = 'studies:session_start'
        return reverse(next_url, args=(pk,))

    def get_back_url(self):
        return reverse('studies:update', args=(self.kwargs['pk'],))


class StudyConsent(AllowErrorsMixin, UpdateView):
    """
    Allows the applicant to add informed consent to their Study
    """
    model = Study
    form_class = StudyConsentForm
    success_message = _('Consent opgeslagen')
    template_name = 'studies/study_consent.html'

    def get_next_url(self):
        proposal = self.object.proposal
        if proposal.studies_number != proposal.study_set.count():
            return reverse('studies:create', args=(proposal.pk,))
        else:
            return reverse('proposals:survey', args=(proposal.pk,))

    def get_back_url(self):
        return reverse('studies:session_end', args=(self.object.pk,))


################
# AJAX callbacks
################
@csrf_exempt
def necessity_required(request):
    """
    This call checks whether the necessity questions are required. They are required when:
    - The researcher requires a supervisor AND one of these cases applies:
        - A selected AgeGroup requires details.
        - Participants have been selected on certain traits.
        - Participants are legally incapable.
    """
    proposal = Proposal.objects.get(pk=request.POST.get('proposal_pk'))
    age_groups = map(int, request.POST.getlist('age_groups[]'))
    has_traits = string_to_bool(request.POST.get('has_traits'))
    legally_incapable = string_to_bool(request.POST.get('legally_incapable'))
    return JsonResponse({'result': check_necessity_required(proposal, age_groups, has_traits, legally_incapable)})
