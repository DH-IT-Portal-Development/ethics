# -*- encoding: utf-8 -*-

from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext as _

from braces.forms import UserKwargModelFormMixin

from core.forms import ConditionalModelForm
from core.utils import YES_NO, YES_NO_DOUBT, get_users_as_list
from .models import Proposal, Wmo


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
        - Don't allow to pick yourself or a superuser as supervisor
        - Don't allow to pick a superuser as applicant
        """
        super(ProposalForm, self).__init__(*args, **kwargs)
        self.fields['relation'].empty_label = None
        self.fields['supervisor'].choices = get_users_as_list(get_user_model().objects.exclude(pk=self.user.pk).exclude(is_superuser=True))
        self.fields['applicants'].choices = get_users_as_list(get_user_model().objects.exclude(is_superuser=True))

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
    study_name_1 = forms.CharField(label=_('Naam traject 1'), max_length=15, required=False)
    study_name_2 = forms.CharField(label=_('Naam traject 2'), max_length=15, required=False)
    study_name_3 = forms.CharField(label=_('Naam traject 3'), max_length=15, required=False)
    study_name_4 = forms.CharField(label=_('Naam traject 4'), max_length=15, required=False)
    study_name_5 = forms.CharField(label=_('Naam traject 5'), max_length=15, required=False)

    class Meta:
        model = Proposal
        fields = ['studies_similar', 'studies_number',
                  'study_name_1', 'study_name_2', 'study_name_3', 'study_name_4', 'study_name_5']
        widgets = {
            'studies_similar': forms.RadioSelect(choices=YES_NO),
        }

    def __init__(self, *args, **kwargs):
        """
        - Set the Proposal for later reference
        - Set studies_similar as required
        - Set initial data for the study_name fields
        """
        self.proposal = kwargs.pop('proposal', None)

        super(StudyStartForm, self).__init__(*args, **kwargs)

        self.fields['studies_similar'].required = True

        for n, study in enumerate(self.proposal.study_set.all()):
            study_name = 'study_name_' + str(n + 1)
            self.fields[study_name].initial = study.name

    def clean(self):
        """
        Check for conditional requirements:
        - If studies_similar is set to False, make sure studies_number is set (and higher than 2)
        - If studies_number is set, make sure the corresponding name fields are filled.
        """
        cleaned_data = super(StudyStartForm, self).clean()

        if not cleaned_data['studies_similar']:
            nr_studies = cleaned_data['studies_number']
            if cleaned_data['studies_number'] < 2:
                self.add_error('studies_number', _('Als niet dezelfde trajecten worden doorlopen, moeten er minstens twee verschillende trajecten zijn.'))
            for n in xrange(nr_studies):
                if n >= 5:
                    break
                study_name = 'study_name_' + str(n + 1)
                if not cleaned_data[study_name]:
                    self.add_error(study_name, _('Dit veld is verplicht.'))


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
