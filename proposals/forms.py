# -*- encoding: utf-8 -*-

from django import forms
from django.contrib.auth import get_user_model
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

from extra_views import InlineFormSet

from core.forms import ConditionalModelForm
from core.utils import YES_NO, YES_NO_DOUBT
from .models import Proposal, Wmo, Study, Survey
from .utils import get_users_as_list


class ProposalForm(ConditionalModelForm):
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
        user = kwargs.pop('user', None)
        super(ProposalForm, self).__init__(*args, **kwargs)
        self.fields['relation'].empty_label = None
        self.fields['supervisor'].queryset = get_user_model().objects.exclude(pk=user.pk, is_superuser=True)
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


class ProposalCopyForm(forms.ModelForm):
    class Meta:
        model = Proposal
        fields = ['parent', 'title']

    def __init__(self, *args, **kwargs):
        """
        Filters the Proposals to only show those where the current User is an applicant.
        """
        user = kwargs.pop('user', None)
        super(ProposalCopyForm, self).__init__(*args, **kwargs)
        self.fields['parent'].queryset = Proposal.objects.filter(applicants=user)


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


class StudyForm(ConditionalModelForm):
    class Meta:
        model = Study
        fields = ['age_groups', 'legally_incapable',
                  'has_traits', 'traits', 'traits_details',
                  'necessity', 'necessity_reason',
                  'recruitment', 'recruitment_details',
                  'setting', 'setting_details',
                  'compensation', 'compensation_details']
        widgets = {
            'age_groups': forms.CheckboxSelectMultiple(),
            'legally_incapable': forms.RadioSelect(choices=YES_NO),
            'has_traits': forms.RadioSelect(choices=YES_NO),
            'traits': forms.CheckboxSelectMultiple(),
            'necessity': forms.RadioSelect(choices=YES_NO_DOUBT),
            'recruitment': forms.CheckboxSelectMultiple(),
            'setting': forms.CheckboxSelectMultiple(),
            'compensation': forms.RadioSelect(),
        }

    def __init__(self, *args, **kwargs):
        """
        - Allow legally_incapable to have HTML in its label
        - Remove empty label from setting/compensation field
        - Set the Proposal for later reference in the clean method
        """
        self.proposal = kwargs.pop('proposal', None)

        super(StudyForm, self).__init__(*args, **kwargs)
        self.fields['legally_incapable'].label = mark_safe(self.fields['legally_incapable'].label)
        self.fields['setting'].empty_label = None
        self.fields['compensation'].empty_label = None

    def clean(self):
        """
        Check for conditional requirements:
        - Check whether necessity/necessity_reason was required and if so, if it has been filled out
        - If has_traits is checked, make sure there is at least one trait selected
        - If a trait which needs details has been checked, make sure the details are filled
        - If a setting which needs details has been checked, make sure the details are filled
        - If a compensation which needs details has been checked, make sure the details are filled
        - If a recruitment which needs details has been checked, make sure the details are filled
        """
        cleaned_data = super(StudyForm, self).clean()

        self.check_necessity_required(cleaned_data)
        self.check_dependency(cleaned_data, 'has_traits', 'traits', _('U dient minimaal een bijzonder kenmerk te selecteren.'))
        self.check_dependency_multiple(cleaned_data, 'traits', 'needs_details', 'traits_details')
        self.check_dependency_multiple(cleaned_data, 'setting', 'needs_details', 'setting_details')
        self.check_dependency_singular(cleaned_data, 'compensation', 'needs_details', 'compensation_details')
        self.check_dependency_multiple(cleaned_data, 'recruitment', 'needs_details', 'recruitment_details')

    def check_necessity_required(self, cleaned_data):
        """
        This call checks whether the necessity questions are required. They are required when:
        - The researcher requires a supervisor AND one of these cases applies:
            - A selected AgeGroup requires details.
            - Participants have been selected on certain traits.
            - Participants are legally incapable.
        """
        if self.proposal.relation.needs_supervisor:
            age_groups = cleaned_data['age_groups']
            neccesity_required = False
            for age_group in age_groups:
                if age_group.needs_details:
                    neccesity_required = True
                    break
            neccesity_required |= cleaned_data['has_traits']
            neccesity_required |= cleaned_data['legally_incapable']
            if neccesity_required:
                if not cleaned_data['necessity_reason']:
                    error = forms.ValidationError(_('Dit veld is verplicht'), code='required')
                    self.add_error('necessity_reason', error)


class StudyConsentForm(forms.ModelForm):
    class Meta:
        model = Study
        fields = ['informed_consent_pdf', 'passive_consent', 'briefing_pdf']
        widgets = {
            'passive_consent': forms.RadioSelect(choices=YES_NO),
        }


class StudyDesignForm(forms.ModelForm):
    class Meta:
        model = Study
        fields = ['has_observation', 'has_intervention', 'has_sessions']

    def clean(self):
        """
        Check for conditional requirements:
        - at least one of the fields has to be checked
        """
        cleaned_data = super(StudyDesignForm, self).clean()
        if not (cleaned_data.get('has_observation') or cleaned_data.get('has_intervention') or cleaned_data.get('has_sessions')):
            msg = _(u'U dient minstens één van de opties te selecteren')
            self.add_error('has_sessions', forms.ValidationError(msg, code='required'))


class StudySurveyForm(forms.ModelForm):
    class Meta:
        model = Study
        fields = ['has_surveys', 'surveys_stressful']
        widgets = {
            'has_surveys': forms.RadioSelect(choices=YES_NO),
            'surveys_stressful': forms.RadioSelect(choices=YES_NO_DOUBT),
        }

    def __init__(self, *args, **kwargs):
        super(StudySurveyForm, self).__init__(*args, **kwargs)
        self.fields['has_surveys'].label = mark_safe(self.fields['has_surveys'].label)


class SurveyInlineFormSet(forms.BaseInlineFormSet):
    """BaseInlineFormSet for Surveys, handles validation"""
    def clean(self):
        cleaned_data = super(SurveyInlineFormSet, self).clean()
        # TODO: add error if no Survey has been provided
        #print cleaned_data
        #raise self.add_error('has_surveys', forms.ValidationError('Foobar'))


class SurveysInline(InlineFormSet):
    """Creates an InlineFormSet for Surveys"""
    model = Survey
    fields = ['name', 'minutes', 'survey_url', 'description']
    can_delete = True
    extra = 1
    formset_class = SurveyInlineFormSet


class SessionStartForm(forms.ModelForm):
    class Meta:
        model = Study
        fields = ['sessions_number']

    def __init__(self, *args, **kwargs):
        """Set the sessions_number field as required"""
        super(SessionStartForm, self).__init__(*args, **kwargs)
        self.fields['sessions_number'].required = True


class SessionEndForm(ConditionalModelForm):
    class Meta:
        model = Study
        fields = ['sessions_duration',
                  'stressful', 'stressful_details',
                  'risk', 'risk_details']
        widgets = {
            'stressful': forms.RadioSelect(choices=YES_NO_DOUBT),
            'risk': forms.RadioSelect(choices=YES_NO_DOUBT),
        }

    def __init__(self, *args, **kwargs):
        """
        - Set sessions_duration as required, update the sessions_duration label
        - Set stressful and risk as required and mark_safe the labels
        - If there is are no Sessions or only one Session in this Study, make the sessions_duration input hidden
        """
        super(SessionEndForm, self).__init__(*args, **kwargs)

        sessions_duration = self.fields['sessions_duration']
        sessions_duration.required = True
        label = sessions_duration.label % self.instance.net_duration()
        sessions_duration.label = mark_safe(label)

        self.fields['stressful'].required = True
        self.fields['risk'].required = True

        self.fields['stressful'].label = mark_safe(self.fields['stressful'].label)
        self.fields['risk'].label = mark_safe(self.fields['risk'].label)

        if not self.instance.has_sessions or self.instance.sessions_number == 1:
            self.fields['sessions_duration'].widget = forms.HiddenInput()

    def clean(self):
        """
        Check for conditional requirements:
        - Check that the net duration is at least equal to the gross duration
        - If stressful is set to yes, make sure stressful_details has been filled out
        - If risk is set to yes, make sure risk_details has been filled out
        """
        cleaned_data = super(SessionEndForm, self).clean()

        # TODO: put this into custom validator
        if self.instance.has_sessions:
            sessions_duration = cleaned_data.get('sessions_duration')
            net_duration = self.instance.net_duration()
            if sessions_duration < net_duration:
                error = forms.ValidationError(_('Totale studieduur moet minstens gelijk zijn aan netto studieduur.'), code='comparison')
                self.add_error('sessions_duration', error)

        self.check_dependency(cleaned_data, 'stressful', 'stressful_details')
        self.check_dependency(cleaned_data, 'risk', 'risk_details')


class ProposalSubmitForm(forms.ModelForm):
    class Meta:
        model = Proposal
        fields = ['comments']
