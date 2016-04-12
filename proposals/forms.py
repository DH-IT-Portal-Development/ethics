# -*- encoding: utf-8 -*-

from django import forms
from django.contrib.auth import get_user_model
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

from braces.forms import UserKwargModelFormMixin
from extra_views import InlineFormSet

from core.forms import ConditionalModelForm
from core.utils import YES_NO, YES_NO_DOUBT
from .models import Proposal, Wmo, Survey
from .utils import get_users_as_list


class ProposalForm(UserKwargModelFormMixin, ConditionalModelForm):
    class Meta:
        model = Proposal
        fields = ['relation', 'supervisor',
                  'other_applicants', 'applicants',
                  'other_stakeholders', 'stakeholders',
                  'date_start', 'title', 'summary',
                  'funding', 'funding_details']
        widgets = {
            'relation': forms.RadioSelect(),
            'other_applicants': forms.RadioSelect(choices=YES_NO),
            'other_stakeholders': forms.RadioSelect(choices=YES_NO),
            'summary': forms.Textarea(attrs={'cols': 50}),
            'funding': forms.CheckboxSelectMultiple()
        }
        error_messages = {
            'title': {
                'unique': _('Er bestaat al een studie met deze titel.'),
            },
        }

    def __init__(self, *args, **kwargs):
        """
        - Remove empty label from relation field
        - Don't allow to pick yourself (or a superuser) as supervisor
        - Retrieve all Users as a nice list
        """
        super(ProposalForm, self).__init__(*args, **kwargs)
        self.fields['relation'].empty_label = None
        self.fields['supervisor'].queryset = get_user_model().objects.exclude(pk=self.user.pk).exclude(is_superuser=True)
        self.fields['applicants'].choices = get_users_as_list()

    def clean(self):
        """
        Check for conditional requirements:
        - If relation needs supervisor, make sure supervisor is set
        - If other_applicants is checked, make sure applicants are set
        - Maximum number of words for summary
        """
        cleaned_data = super(ProposalForm, self).clean()

        relation = cleaned_data.get('relation')
        if relation and relation.needs_supervisor and not cleaned_data.get('supervisor'):
            error = forms.ValidationError(_('U dient een eindverantwoordelijke op te geven.'), code='required')
            self.add_error('supervisor', error)

        if cleaned_data.get('other_applicants') and len(cleaned_data.get('applicants')) == 1:
            error = forms.ValidationError(_('U heeft geen andere onderzoekers geselecteerd.'), code='required')
            self.add_error('applicants', error)

        self.check_dependency(cleaned_data, 'other_stakeholders', 'stakeholders',
                              _('U heeft geen andere betrokkenen genoemd.'))

        self.check_dependency_multiple(cleaned_data, 'funding', 'needs_details', 'funding_details')


class ProposalCopyForm(UserKwargModelFormMixin, forms.ModelForm):
    class Meta:
        model = Proposal
        fields = ['parent', 'title']

    def __init__(self, *args, **kwargs):
        """
        Filters the Proposals to only show those where the current User is an applicant.
        """
        super(ProposalCopyForm, self).__init__(*args, **kwargs)
        self.fields['parent'].queryset = Proposal.objects.filter(applicants=self.user)


class WmoForm(ConditionalModelForm):
    class Meta:
        model = Wmo
        fields = ['metc', 'metc_institution', 'is_medical', 'is_behavioristic',
                  'metc_application', 'metc_decision', 'metc_decision_pdf']
        widgets = {
            'metc': forms.RadioSelect(choices=YES_NO_DOUBT),
            'is_medical': forms.RadioSelect(choices=YES_NO_DOUBT),
            'is_behavioristic': forms.RadioSelect(choices=YES_NO_DOUBT),
            'metc_application': forms.RadioSelect(choices=YES_NO),
            'metc_decision': forms.RadioSelect(choices=YES_NO),
        }

    def clean(self):
        """
        Check for conditional requirements:
        - If metc is checked, make sure institution is set
        """
        cleaned_data = super(WmoForm, self).clean()

        self.check_dependency(cleaned_data, 'metc', 'metc_institution',
                              _('U dient een instelling op te geven.'))


class WmoCheckForm(forms.ModelForm):
    class Meta:
        model = Wmo
        fields = ['metc', 'is_medical', 'is_behavioristic']
        widgets = {
            'metc': forms.RadioSelect(choices=YES_NO_DOUBT),
            'is_medical': forms.RadioSelect(choices=YES_NO_DOUBT),
            'is_behavioristic': forms.RadioSelect(choices=YES_NO_DOUBT),
        }


class StudyStartForm(forms.ModelForm):
    class Meta:
        model = Proposal
        fields = ['has_multiple_groups',
                  'has_multiple_trajectories',
                  'studies_number']
        widgets = {
            'has_multiple_groups': forms.RadioSelect(choices=YES_NO),
            'has_multiple_trajectories': forms.RadioSelect(choices=YES_NO),
        }

    def __init__(self, *args, **kwargs):
        """
        - Set has_multiple_groups as required.
        """
        super(StudyStartForm, self).__init__(*args, **kwargs)

        self.fields['has_multiple_groups'].required = True


class ProposalSurveyForm(forms.ModelForm):
    class Meta:
        model = Proposal
        fields = ['has_surveys', 'surveys_stressful']
        widgets = {
            'has_surveys': forms.RadioSelect(choices=YES_NO),
            'surveys_stressful': forms.RadioSelect(choices=YES_NO_DOUBT),
        }

    def __init__(self, *args, **kwargs):
        super(ProposalSurveyForm, self).__init__(*args, **kwargs)
        self.fields['has_surveys'].label = mark_safe(self.fields['has_surveys'].label)


class SurveyInlineFormSet(forms.BaseInlineFormSet):
    def clean(self):
        """
        - If has_surveys has been set, there should be at least one Survey
        - If has_surveys has not been set, remove all validation errors
        """
        if self.instance.has_surveys:
            count = 0
            for form in self.forms:
                cleaned_data = form.cleaned_data
                if cleaned_data and not cleaned_data.get('DELETE', False):
                    count += 1

            if count == 0:
                first_form = self.forms[0]
                error = forms.ValidationError(_(u'U dient op zijn minst één vragenlijst toe te voegen.'), code='required')
                if first_form.is_valid():
                    first_form.add_error('name', error)
                else:
                    # TODO: find a way to show this error in the template
                    raise error
        else:
            for form in self.forms:
                form._errors = []


class SurveysInline(InlineFormSet):
    """Creates an InlineFormSet for Surveys"""
    model = Survey
    fields = ['name', 'minutes', 'survey_url', 'description']
    can_delete = True
    extra = 1
    formset_class = SurveyInlineFormSet


class ProposalSubmitForm(forms.ModelForm):
    class Meta:
        model = Proposal
        #fields = ['informed_consent', 'briefing', 'comments']
        fields = ['comments']

    def __init__(self, *args, **kwargs):
        """Set the consent fields as required"""
        super(ProposalSubmitForm, self).__init__(*args, **kwargs)

        """
        TODO: fix this!
        proposal = self.instance
        if not proposal.informed_consent:
            self.fields['informed_consent'].required = True
        else:
            del self.fields['informed_consent']

        if not proposal.briefing_pdf:
            self.fields['briefing'].required = True
        else:
            del self.fields['briefing']
        """
