# -*- encoding: utf-8 -*-

from django import forms
from django.contrib.auth import get_user_model
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

from extra_views import InlineFormSet

from .models import Proposal, Wmo, Study, Session, Task, Survey
from .utils import check_dependency, check_dependency_singular, check_dependency_multiple, get_users_as_list

YES_NO = [(True, _('ja')), (False, _('nee'))]
YES_NO_DOUBT = [(True, _('ja')), (False, _('nee')), (None, _('twijfel'))]
SUMMARY_MAX_WORDS = 200


class ProposalForm(forms.ModelForm):
    class Meta:
        model = Proposal
        fields = ['relation', 'supervisor',
                  'other_applicants', 'applicants',
                  'other_stakeholders', 'stakeholders',
                  'date_start', 'date_end',
                  'title', 'summary',
                  'funding', 'funding_details']
        widgets = {
            'relation': forms.RadioSelect(),
            'other_applicants': forms.RadioSelect(choices=YES_NO),
            'other_stakeholders': forms.RadioSelect(choices=YES_NO),
            'summary': forms.Textarea(attrs={'rows': 30, 'cols': 80}),
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

        check_dependency(self, cleaned_data, 'other_stakeholders', 'stakeholders',
                         _('U heeft geen andere betrokkenen genoemd.'))

        # TODO: turn into custom validator
        summary = cleaned_data.get('summary')
        if summary and len(summary.split()) > SUMMARY_MAX_WORDS:
            error = forms.ValidationError(_('De samenvatting bestaat uit teveel woorden.'), code='max')
            self.add_error('summary', error)

        check_dependency_multiple(self, cleaned_data, 'funding', 'needs_details', 'funding_details')


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


class WmoForm(forms.ModelForm):
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

        check_dependency(self, cleaned_data, 'metc', 'metc_institution',
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


class StudyForm(forms.ModelForm):
    class Meta:
        model = Study
        fields = ['age_groups', 'legally_incapable',
                  'has_traits',
                  'necessity', 'necessity_reason',
                  'recruitment', 'recruitment_details',
                  'setting', 'setting_details',
                  'compensation', 'compensation_details',
                  'informed_consent_pdf', 'passive_consent', 'briefing_pdf']
        widgets = {
            'age_groups': forms.CheckboxSelectMultiple(),
            'legally_incapable': forms.RadioSelect(choices=YES_NO),
            'has_traits': forms.RadioSelect(choices=YES_NO),
            'necessity': forms.RadioSelect(choices=YES_NO_DOUBT),
            'recruitment': forms.CheckboxSelectMultiple(),
            'setting': forms.CheckboxSelectMultiple(),
            'compensation': forms.RadioSelect(),
            'passive_consent': forms.RadioSelect(choices=YES_NO)
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
        - If a setting which needs details has been checked, make sure the details are filled
        - If a compensation which needs details has been checked, make sure the details are filled
        - If a recruitment which needs details has been checked, make sure the details are filled
        """
        cleaned_data = super(StudyForm, self).clean()

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

        check_dependency_multiple(self, cleaned_data, 'setting', 'needs_details', 'setting_details')
        check_dependency_singular(self, cleaned_data, 'compensation', 'needs_details', 'compensation_details')
        check_dependency_multiple(self, cleaned_data, 'recruitment', 'needs_details', 'recruitment_details')


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
        if not (cleaned_data.get('has_observation')
                or cleaned_data.get('has_intervention')
                or cleaned_data.get('has_sessions')):
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


class TaskStartForm(forms.ModelForm):
    is_copy = forms.BooleanField(
        label=_('Is deze sessie een kopie van een voorgaande sessie?'),
        help_text=_(u'Na het kopiëren zijn alle velden bewerkbaar.'),
        widget=forms.RadioSelect(choices=YES_NO),
        initial=False,
        required=False)
    parent_session = forms.ModelChoiceField(
        label=_(u'Te kopiëren sessie'),
        queryset=Session.objects.all(),
        required=False)

    class Meta:
        model = Session
        fields = ['tasks_number']

    def __init__(self, *args, **kwargs):
        """
        - The field tasks_number is not required by default (only is is_copy is set to False)
        - Only allow to choose earlier Sessions
        - Remove option to copy altogether from first Session
        """
        super(TaskStartForm, self).__init__(*args, **kwargs)
        self.fields['tasks_number'].required = False
        self.fields['parent_session'].queryset = Session.objects.filter(study=self.instance.study.pk,
                                                                        order__lt=self.instance.order)

        if self.instance.order == 1:
            del self.fields['is_copy']
            del self.fields['parent_session']

    def clean(self):
        """
        Check for conditional requirements:
        - If is_copy is True, parent_session is required
        - If is_copy is False, tasks_number is required
        """
        cleaned_data = super(TaskStartForm, self).clean()

        check_dependency(self, cleaned_data, 'is_copy', 'parent_session')
        if not cleaned_data.get('is_copy') and not cleaned_data.get('tasks_number'):
            self.add_error('tasks_number', forms.ValidationError(_('Dit veld is verplicht'), code='required'))


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['name', 'description', 'duration',
                  'registrations', 'registrations_details',
                  'registration_kinds', 'registration_kinds_details',
                  'feedback', 'feedback_details',
                  'deception', 'deception_details']
        widgets = {
            'registrations': forms.CheckboxSelectMultiple(),
            'registration_kinds': forms.CheckboxSelectMultiple(),
            'feedback': forms.RadioSelect(choices=YES_NO),
            'deception': forms.RadioSelect(choices=YES_NO),
        }

    def __init__(self, *args, **kwargs):
        super(TaskForm, self).__init__(*args, **kwargs)
        self.fields['duration'].label = mark_safe(self.fields['duration'].label)

    def clean(self):
        """
        Check for conditional requirements:
        - If a registration which needs a kind has been checked, make sure the kind is selected
        - If a registration which needs details has been checked, make sure the details are filled
        - If a registration_kind which needs details has been checked, make sure the details are filled
        - If feedback is set to yes, make sure feedback_details has been filled out
        - If deception is set to yes, make sure deception_details has been filled out
        """
        cleaned_data = super(TaskForm, self).clean()

        check_dependency_multiple(self, cleaned_data, 'registrations', 'needs_kind', 'registration_kinds')
        check_dependency_multiple(self, cleaned_data, 'registrations', 'needs_details', 'registrations_details')
        check_dependency_multiple(self, cleaned_data, 'registration_kinds', 'needs_details', 'registration_kinds_details')
        check_dependency(self, cleaned_data, 'feedback', 'feedback_details')
        check_dependency(self, cleaned_data, 'deception', 'deception_details')


class TaskEndForm(forms.ModelForm):
    class Meta:
        model = Session
        fields = ['tasks_duration']

    def __init__(self, *args, **kwargs):
        """
        - Set the tasks_duration label
        - Set the tasks_duration as required
        """
        super(TaskEndForm, self).__init__(*args, **kwargs)

        tasks_duration = self.fields['tasks_duration']
        tasks_duration.required = True
        label = tasks_duration.label % self.instance.net_duration()
        tasks_duration.label = mark_safe(label)

    def clean(self):
        """
        Check for conditional requirements:
        - Check that the net duration is at least equal to the gross duration
        """
        cleaned_data = super(TaskEndForm, self).clean()

        # TODO: put this into custom validator
        tasks_duration = cleaned_data.get('tasks_duration')
        net_duration = self.instance.net_duration()
        if tasks_duration < net_duration:
            error = forms.ValidationError(_('Totale sessieduur moet minstens gelijk zijn aan netto sessieduur.'), code='comparison')
            self.add_error('tasks_duration', error)


class SessionEndForm(forms.ModelForm):
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

        check_dependency(self, cleaned_data, 'stressful', 'stressful_details')
        check_dependency(self, cleaned_data, 'risk', 'risk_details')


class ProposalSubmitForm(forms.ModelForm):
    class Meta:
        model = Proposal
        fields = ['comments']
