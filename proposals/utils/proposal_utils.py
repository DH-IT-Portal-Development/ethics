# -*- encoding: utf-8 -*-

from collections import defaultdict, OrderedDict
from datetime import datetime, date
from io import BytesIO
import os

from django.conf import settings
from django.contrib.staticfiles import finders
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage
from django.core.mail import send_mail
from django.db.models import Q
from django.urls import reverse
from django.template.loader import render_to_string, get_template
from django.utils.translation import activate, get_language, ugettext as _
from django.utils.deconstruct import deconstructible

from main.utils import AvailableURL, get_secretary
from studies.utils import study_urls


__all__ = ['available_urls', 'generate_ref_number',
           'generate_revision_ref_number', 'generate_pdf',
           'check_local_facilities', 'notify_local_staff',
           'FilenameFactory', 'OverwriteStorage',
           ]


def available_urls(proposal):
    """
    Returns the available URLs for the given Proposal.
    :param proposal: the current Proposal
    :return: a list of available URLs for this Proposal.
    """
    urls = list()

    if proposal.is_pre_assessment:
        urls.append(AvailableURL(url=reverse('proposals:update_pre', args=(proposal.pk,)),
                                 title=_('Algemene informatie over de aanvraag')))

        wmo_url = AvailableURL(title=_('Ethische toetsing nodig door een METC?'))
        if hasattr(proposal, 'wmo'):
            wmo_url.url = reverse('proposals:wmo_update_pre', args=(proposal.wmo.pk,))
        else:
            wmo_url.url = reverse('proposals:wmo_create_pre', args=(proposal.pk,))
        urls.append(wmo_url)

        submit_url = AvailableURL(title=_('Aanvraag voor voortoetsing klaar voor versturen'))
        if hasattr(proposal, 'wmo'):
            submit_url.url = reverse('proposals:submit_pre', args=(proposal.pk,))
        urls.append(submit_url)
    elif proposal.is_pre_approved:
        urls.append(AvailableURL(url=reverse('proposals:update_pre_approved', args=(proposal.pk,)),
                                 title=_('Algemene informatie over de aanvraag')))

        submit_url = AvailableURL(
            title=_('Aanvraag voor voortoetsing klaar voor versturen'),
            margin=0,
            url = reverse('proposals:submit_pre_approved', args=(proposal.pk,))
        )
        urls.append(submit_url)
    else:
        update_url = 'proposals:update_practice' if proposal.is_practice() else 'proposals:update'
        urls.append(
            AvailableURL(
                url=reverse(update_url, args=(proposal.pk,)),
                title=_('Algemeen'),
            )
        )

        wmo_url = AvailableURL(
            title=_('METC')
        )
        if hasattr(proposal, 'wmo'):
            wmo_url.url = reverse(
                'proposals:wmo_update',
                args=(proposal.wmo.pk,)
            )
        else:
            wmo_url.url = reverse(
                'proposals:wmo_create',
                args=(proposal.pk,)
            )
        urls.append(wmo_url)

        studies_url = AvailableURL(title=_('Trajecten'))
        if hasattr(proposal, 'wmo'):
            studies_url.url = reverse(
                        'proposals:study_start',
                        args=(proposal.pk,)
                    )

            if proposal.study_set.count() > 0:
                _add_study_urls(studies_url, proposal)

        urls.append(studies_url)

        consent_docs_url = AvailableURL(
            title=_('Uploaden'), 
            url=reverse(
                'proposals:consent', 
                args=(proposal.pk, )
                )
            )
        translated_docs_url = AvailableURL(
            title=_('Vertaling'), 
            url=reverse(
                'proposals:translated', 
                args=(proposal.pk, )
                )
            )
        consent_url = AvailableURL(
            title=_('Formulieren'), 
            children=[
                translated_docs_url, 
                consent_docs_url
                ]
            )

        data_management_url = AvailableURL(title=_('Datamanagement'))
        submit_url = AvailableURL(title=_('Versturen'))

        if proposal.last_study() and proposal.last_study().is_completed():
            consent_url.url = reverse('proposals:translated', args=(proposal.pk, ))
            data_management_url.url = reverse('proposals:data_management', args=(proposal.pk, ))
            submit_url.url = reverse('proposals:submit', args=(proposal.pk,))

        if proposal.translated_forms is not None:
            consent_url.url = reverse('proposals:consent', args=(proposal.pk,))

        urls.append(consent_url)
        urls.append(data_management_url)
        urls.append(submit_url)

    return urls


def _add_study_urls(main_element, proposal):
    # If only one trajectory, add the children urls of that study directly.
    # (Bypassing the study's own node)
    if proposal.studies_number == 1:
        main_element.children.extend(
            study_urls(proposal.study_set.first(), True).children
        )
        return

    # Otherwise, add them all with the parent node
    prev_study_completed = True
    for study in proposal.study_set.all():
        main_element.children.append(
            study_urls(study, prev_study_completed)
        )
        prev_study_completed = study.is_completed()


def generate_ref_number():
    """
    Generates a reference number for a new(!) Proposal.
    NOTE: Use generate_revision_ref_number to create reference numbers for
    revisions! This function will always create a new ref.num. with version = 1
    :return: a reference number in the format {nr}-{vr}-{current_year},
    where nr is the number of Proposals created  in the current year excluding
    revisions. Vr is the version of this proposal, this function will always return vr = 1.
    """
    # Set default values
    current_year = datetime.now().year
    current_year_formatted = str(current_year)[2:]
    proposal_number = _get_next_proposal_number(current_year)
    version_number = 1

    return '{}-{:03}-{:02}'.format(
        current_year_formatted,
        proposal_number,
        version_number,
    )


def generate_revision_ref_number(parent):
    """
    Generates a new reference number for revisions of a proposal.
    This is done by looking up the last revision of the specified proposal,
    not by incrementing the version of the specified proposal.
    (The latter will fail spectacularly when a user makes 2 revisions from the
    same proposal)
    Note: this function uses two helper functions
    :param parent: The proposal that will be revised
    :return: a reference number in the format {year}-{nr}-{vr}, where nr is the
    number of Proposals created by the current User in the current year
    excluding revisions. This method will use the same nr as the parent. Vr
    is the version of this proposal, this function
    will use the next available version number (this might not be the same as
    parent.vr + 1, as that one might already exist).
    """
    parent_parts = parent.reference_number.split('-')

    # If we have 4 parts, the ref.number is in the user-nr-vr-year format
    if len(parent_parts) == 4:
        return _generate_revision_ref_number_oldformat(parent, 2)
    # If the first part is longer than 2 characters, it's the usr-nr-year format
    elif len(parent_parts[0]) > 2:
        # Otherwise, we assume it's in the old user-nr-year format
        return _generate_revision_ref_number_oldformat(parent, 1)

    return _generate_revision_ref_number_newformat(parent)


def _generate_revision_ref_number_oldformat(parent, version):
    """This method generates a new reference number from proposals using
    an older version of the ref.num.
    """
    from ..models import Proposal

    parent_parts = parent.reference_number.split('-')

    old_proposal_number = int(parent_parts[1])
    proposal_number = -1
    year = -1

    # Version 2 is the user-nr-vr-year format
    if version == 2:
        year = parent_parts[3]
        proposal_number = _get_next_proposal_number(int(year))
    # Version 1 is the usr-nr-year format
    elif version == 1:
        # Otherwise, we assume it's in the old user-nr-year format
        year = parent_parts[2]
        proposal_number = _get_next_proposal_number(int(year))

    username = parent.created_by.username

    # Count all proposals by matching all proposals with the same user-nr
    # part and the same year. (This way we find both old and new style ref.nums)
    num_versions = Proposal.objects.filter(
        Q(
            reference_number__istartswith="{}-{:02}".format(username,
                                                            old_proposal_number),
            reference_number__endswith=str(year)
        ) | Q(reference_number__istartswith="{}-{:03}".format(year,
                                                              proposal_number))

    ).count()

    # The new revision is number of current versions + 1
    version_number = num_versions + 1

    return '{}-{:03}-{:02}'.format(
        year[2:],
        proposal_number,
        version_number,
    )


def _generate_revision_ref_number_newformat(parent):
    """This method generates a new reference number from proposals using
    the current version of the ref.num.
    """
    from ..models import Proposal

    parent_parts = parent.reference_number.split('-')
    year = int(parent_parts[0])
    proposal_number = int(parent_parts[1])

    # Get all proposals with this reference number (excluding version number)
    parent_proposals = Proposal.objects.filter(
        reference_number__istartswith="{}-{:03}".format(year, proposal_number)
    )

    # Loop through all them, and note the newest version seen
    newest = None
    for parent_proposal in parent_proposals:
        version = parent_proposal.reference_number.split('-')[2]
        version = int(version)
        if not newest or version > newest:
            newest = version

    version_number = newest + 1

    return '{}-{:03}-{:02}'.format(
        year,
        proposal_number,
        version_number,
    )


def _get_next_proposal_number(current_year) -> int:
    from ..models import Proposal

    try:
        # We count all proposals for this year by selecting all proposals
        # with a reference number ending with the current year.
        last_proposal = Proposal.objects.filter(
            reference_number__startswith="{}-".format(str(current_year)[2:])
        ).order_by('-reference_number').first()

        if not last_proposal:
            return 1

        _, num, _ = last_proposal.reference_number.split('-', maxsplit=2)

        return int(num) + 1
    except Proposal.DoesNotExist:
        return 1

from django.contrib.auth import get_user_model
from django.utils.safestring import mark_safe
from django.utils.html import format_html
from copy import copy
from django.conf import settings
from proposals.templatetags.proposal_filters import needs_details, medical_traits, \
necessity_required, has_adults

'''NOTE TO SELF:
Might not  have to have the whole tuple system ...
Would streamline code a lot.'''

'''TODO: Test multiple studies proposal'''

class PDFSection:
    
    section_title = None
    study_title = None
    row_fields = None
    verbose_name_diff_field_dict = {
        'get_metc_display': 'metc',
        'get_is_medical_display': 'is_medical'
    }

    def __init__(self, object):
        self.object = object
        # Create a copy of the class level row_fields, such that we can safely manipulate it without changing the class value
        self._row_fields = copy(self.row_fields)
    
    def get_rows(self):
        rows = OrderedDict()
        for row_field in self._row_fields:
            if row_field in self.verbose_name_diff_field_dict:
                verbose_name = self.verbose_name_diff_field_dict[row_field]
                '''This sequence checks for all combinations of tuples and strings
                in the dict. Might not be neccessary, but is nice to account
                for all possibilities'''
                if type(row_field) == str and type(verbose_name) == str:
                    rows[row_field] = {
                    'label': self.object._meta.get_field(verbose_name).verbose_name,
                    'value': RowValueClass(self.object, row_field).render()
                    }
                elif type(row_field) == tuple and type(verbose_name) == str:
                    rows[row_field[-1]] = {
                    'label': self.object._meta.get_field(verbose_name).verbose_name,
                    'value': RowValueClass(self.object, row_field).render()
                    }  
                elif type(row_field) == str and type(verbose_name) == tuple:
                    rows[row_field] = {
                    'label': self.get_nested_verbose_name(self.object, verbose_name),
                    'value': RowValueClass(self.object, row_field).render()
                    }
                else:
                    rows[row_field[-1]] = {
                    'label': self.get_nested_verbose_name(self.object, verbose_name),
                    'value': RowValueClass(self.object, row_field).render()
                    }  
            else:
                if type(row_field) == str:
                    rows[row_field] = {
                    'label': self.object._meta.get_field(row_field).verbose_name,
                    'value': RowValueClass(self.object, row_field).render()
                    }
                elif type(row_field) == tuple:
                    rows[row_field[-1]] = {
                    'label': self.get_nested_verbose_name(self.object, row_field),
                    'value': RowValueClass(self.object, row_field).render()
                    }
        return rows

    def render(self, context):
        template = get_template("proposals/pdf/table_with_header.html")
        context.update(
            {
                "section_title": self.section_title,
                "rows": self.get_rows(),
            }
        )

        return template.render(context.flatten())
    
    def get_nested_verbose_name(self, object, tuple_field):
        for item in tuple_field:
            if item == tuple_field[-1]:
                verbose_name = object._meta.get_field(item).verbose_name 
                break
            new_object = getattr(object, item)
            object = new_object
        return verbose_name
    
    def get_study_title(self, study):
        if study.name:
            study_title = format_html('{}{}{}{}{}',
                                      _('Traject '),
                                      study.order,
                                      mark_safe(' <em>'),
                                      study.name,
                                      mark_safe(' </em>')
            )
        else:
            study_title = format_html('{}{}',
                                      _('Traject'),
                                      {study.order}
            )
        return study_title
    
    def get_session_title(self, session):

        order = session.order 
        study_order = session.study.order 
        study_name = session.study.name 
        studies_number = session.study.proposal.studies_number 
        sessions_number = session.study.sessions_number

        if studies_number > 1 and sessions_number > 1:
            session_title = format_html('{}{}{}{}{}{}{}',
                                      _('Traject '),
                                      study_order,
                                      mark_safe(' <em>'),
                                      study_name,
                                      mark_safe(' </em>, '),
                                      _('sessie '),
                                      order
            )
        elif studies_number > 1:
            session_title = format_html('{}{}{}{}{}',
                                      _('Traject '),
                                      study_order,
                                      mark_safe(' <em>'),
                                      study_name,
                                      mark_safe(' </em>')
            )
        elif sessions_number >= 1:
            session_title = format_html('{}{}',
                                        _('Sessie '),
                                        order
            )
        return session_title
    
    def get_task_title(task):
        order=task.order 
        session_order=task.session.order 
        study_order=task.session.study.order 
        study_name=task.session.study.name 
        studies_number=task.session.study.proposal.studies_number
        if studies_number > 1:
            task_title = format_html('{}{}{}{}{}{}{}{}{}',
                                      _('Traject '),
                                      study_order,
                                      mark_safe(' <em>'),
                                      study_name,
                                      mark_safe(' </em>, '),
                                      _('sessie '),
                                      session_order,
                                      _(', taak '),
                                      order
            )
        else:
            task_title = format_html('{}{}{}{}',
                                     _('Sessie '),
                                     session_order,
                                     _(', taak '),
                                     order
                                     )
        return task_title

class GeneralSection(PDFSection):
    '''This class generates the data for the general section of 
    the PDF page.'''

    section_title = _("Algemene informatie over de aanvraag")
    row_fields = [
        'relation',
        'supervisor',
        'student_program',
        'student_context',
        'student_context_details',
        'student_justification',
        'other_applicants',
        'applicants',
        'other_stakeholders',
        'stakeholders',
        'date_start',
        'title',
        'funding',
        'funding_details',
        'funding_name',
        'self_assessment',
    ]
    
    def get_rows(self):
        obj = self.object
        rows = self._row_fields
        if not obj.relation.needs_supervisor:
            rows.remove('supervisor')
        if not obj.relation.check_in_course:
            rows.remove('student_program')
            rows.remove('student_context')
            if obj.student_context is not None:
                if not obj.student_context.needs_details:
                    rows.remove('student_context_details')
            else:
                rows.remove('student_context_details')
            rows.remove('student_justification')
        if not obj.other_applicants:
            rows.remove('applicants')
        if not obj.other_stakeholders:
            rows.remove('stakeholders')
        if not needs_details(obj.funding.all()):
            rows.remove('funding_details')
        if not needs_details(obj.funding.all(), 'needs_name'):
            rows.remove('funding_name')
        # Use the get_rows from PDFSection to get the actual rows, the code above should have filtered out everything we don't need
        return super().get_rows()
    
class WMOSection(PDFSection):
    '''Object for this section is proposal.wmo'''
    section_title = _("Ethische toetsing nodig door een Medische Ethische Toetsingscommissie (METC)?")
    row_fields = [
        'get_metc_display',
        'metc_details',
        'metc_institution',
        'get_is_medical_display',  
    ]
    
    def get_rows(self):
        obj = self.object
        rows = self._row_fields
        if not obj.metc == 'Y':
            rows.remove('metc_details')
            rows.remove('metc_institution')
        else:
            rows.remove('get_is_medical_display')
        return super().get_rows()
    
class METCSection(PDFSection):
    '''Object for this section is proposal.wmo'''
    section_title = _("Aanmelding bij de METC")
    
    row_fields = [
        'metc_application',
        'metc_decision',
        'metc_decision_pdf'
    ]
    
class TrajectoriesSection(PDFSection):

    section_title = _("Eén of meerdere trajecten?")

    row_fields = [
        'studies_similar',
        'studies_number'
    ]
    
    def get_rows(self):
        obj = self.object
        rows = self._row_fields
        if obj.studies_similar:
            rows.remove('studies_number')
        return super().get_rows()
    
class StudySection(PDFSection):
    '''object for this study is proposal.study'''
    section_title = _('De Deelnemers')
    row_fields = [
        'age_groups',
        'legally_incapable',
        'legally_incapable_details',
        'has_special_details',
        'special_details',
        'traits',
        'traits_details',
        'necessity',
        'necessity_reason',
        'recruitment',
        'recruitment_details',
        'compensation',
        'compensation_details',
        'hierarchy',
        'hierarchy_details',
    ]

    def get_rows(self):
        obj = self.object
        rows = self._row_fields
        if not has_adults(obj):
            rows.remove('legally_incapable')
            rows.remove('legally_incapable_details')
        elif not obj.legally_incapable:
            rows.remove('legally_incapable_details')
        if not obj.has_special_details:
            rows.remove('special_details')
            rows.remove('traits')
            rows.remove('traits_details')
        elif not medical_traits(obj.special_details.all()):
            rows.remove('traits')
            rows.remove('traits_details')
        elif not needs_details(obj.traits.all()):
            rows.remove('traits_details')
        if not necessity_required(obj):
            rows.remove('necessity')
            rows.remove('necessity_reason')
        if not needs_details(obj.recruitment.all()):
            rows.remove('recruitment_details')
        if not obj.compensation.needs_details:
            rows.remove('compensation_details')
        if not obj.hierarchy:
            rows.remove('hierarchy_details')
        return super().get_rows()
        
    def render(self, context):
        if self.object.proposal.studies_number > 1:
            context.update(
                {
                    'study_title': super().get_study_title(self.object)
                }
            )
        return super().render(context)

class InterventionSection(PDFSection):
    '''This class will receive a intervention object'''
    section_title = _('Het interventieonderzoek')
    row_fields = [
        'setting',
        'setting_details',
        'supervision',
        'leader_has_coc',
        'period',
        'multiple_sessions', 
        'session_frequency',
        'amount_per_week',
        'duration',
        'measurement',
        'experimenter',
        'description',
        'has_controls',
        'controls_description',
        'extra_task'
    ]

    def get_rows(self):
        obj = self.object
        rows = self._row_fields

        if obj.version == 1:
            fields_to_remove = ['multiple_sessions',
                                'session_frequency',
                                'extra_task']
            for field in fields_to_remove:
                rows.remove(field)
        else:
            rows.remove('amount_per_week')
            if not obj.multiple_sessions:
                rows.remove('session_frequency')
            if obj.settings_contains_schools:
                rows.remove('extra_task')
        
        if not needs_details(obj.setting.all()):
            rows.remove('setting_details')
        if not obj.study.has_children() or \
        not needs_details(obj.setting.all(), 'needs_supervision'):
            rows.remove('supervision')
            rows.remove('leader_has_coc')
        elif obj.supervision:
            rows.remove('leader_has_coc')
        if not obj.has_controls:
            rows.remove('controls_description')          

        return super().get_rows()
    
    def render(self, context):
        if self.object.study.proposal.studies_number > 1:
            context.update(
                {
                    'study_title': super().get_study_title(self.object.study)
                }
            )
        return super().render(context)
    
class ObservationSection(InterventionSection):
    '''Gets passed an observation object'''
    section_title = _('Het observatieonderzoek')
    row_fields = [
        'setting',
        'setting_details',
        'supervision',
        'leader_has_coc',
        'days',
        'mean_hours',
        'details_who',
        'details_why',
        'details_frequency',
        'is_anonymous',
        'is_anonymous_details',
        'is_in_target_group',
        'is_in_target_group_details',
        'is_nonpublic_space',
        'is_nonpublic_space_details',
        'has_advanced_consent',
        'has_advanced_consent_details',
        'needs_approval',
        'approval_institution',
        'approval_document',
        'registrations',
        'registrations_details'        
    ]

    def get_rows(self):
        obj = self.object
        rows = self._row_fields

        if obj.version == 1:
            to_remove_if_v1 = ['details_who',
                            'details_why',
                            'is_anonymous_details', 
                            'is_in_target_group_details',
                            'is_nonpublic_space_details',
                            'has_advanced_consent_details'
                            ]
            for field in to_remove_if_v1:
                rows.remove(field)

            if not obj.is_nonpublic_space:
                rows.remove('has_advanced_consent')
            if not obj.needs_approval:
                rows.remove('approval_institution')
                rows.remove('approval_document')
            elif obj.study.proposal.is_practice():
                rows.remove('approval_document')
        else:
            to_remove_if_v2 = ['days', 'mean_hours', 'approval_document']
            for field in to_remove_if_v2:
                rows.remove(field)

            if not obj.is_anonymous:
                rows.remove('is_anonymous_details')
            if not obj.is_in_target_group:
                rows.remove('is_in_target_group_details')
            if not obj.is_nonpublic_space:
                rows.remove('is_nonpublic_space_details')
                rows.remove('has_advanced_consent')
                rows.remove('has_advanced_consent_details')
            elif obj.has_advanced_consent:
                rows.remove('has_advanced_consent_details')
            if not needs_details(obj.setting.all(), 'is_school'):
                rows.remove('needs_approval')
            if not obj.needs_approval:
                rows.remove('approval_institution')

        if not needs_details(obj.setting.all()):
            rows.remove('setting_details')
        if not obj.study.has_children() or \
        not needs_details(obj.setting.all(), 'needs_supervision'):
            rows.remove('supervision')
            rows.remove('leader_has_coc')
        elif obj.supervision:
            rows.remove('leader_has_coc')
        if not needs_details(obj.registrations.all()):
            rows.remove('registrations_details')

        return super(InterventionSection, self).get_rows()

class SessionsSection(StudySection):
    '''Gets passed a study object'''
    section_title = _("Het takenonderzoek en interviews")
    row_fields = ['sessions_number']

    def get_rows(self):
        return super(StudySection, self).get_rows()

class SessionSection(PDFSection):
    '''Gets passed a session object'''
    
    row_fields = [
        'setting',
        'setting_details',
        'supervision',
        'leader_has_coc',
        'tasks_number',       
    ]

    def get_rows(self):
        obj = self.object
        rows = self._row_fields

        if not needs_details(obj.setting.all()):
            rows.remove('setting_details')
        if not obj.study.has_children() or \
        not needs_details(obj.setting.all(), 'needs_supervision'):
            rows.remove('supervision')
            rows.remove('leader_has_coc')
        elif obj.supervision:
            rows.remove('leader_has_coc')

        return super().get_rows()
    
    def render(self, context):
        context.update(
            {
                'study_title': super().get_session_title(self.object)
            }
        )
        return super().render(context)
    
class TaskSection(PDFSection):
    '''Gets passed a task object'''
    
    row_fields = [
    
    ]

    def get_rows(self):
        obj = self.object
        rows = self._row_fields

        return super().get_rows()
    
    def render(self, context):
        context.update(
            {
                'study_title': super().get_task_title(self.object)
            }
        )
        return super().render(context)




class RowValueClass:

    def __init__(self, object, field):

        self.object = object
        self.field = field

    def render(self):
        from ..models import Funding, Relation

        if type(self.field) == str:
            value = getattr(self.object, self.field)
        '''A workaround for accessing subclasses:
        For a subclass provide a tuple like so:
        ('wmo', 'metc')'''
        if type(self.field) == tuple:
            object = self.object
            for item in self.field:
                value = getattr(object, item)
                object = value

        User = get_user_model()

        if type(value) in (str, int, date):
            return value
        if value is None:
            return _('Onbekend')
        elif type(value) == bool:
            return _('Ja') if value else _('Nee')
        elif type(value) == User:
            return self.handle_user(value)
        elif type(value) == Relation:
            return value.description
        elif value.__class__.__name__ == 'ManyRelatedManager':
            if value.all().model == User:
                return self.get_applicants_names(value)
            else:
                return self.get_object_list(value)
        elif value.__class__.__name__ == 'FieldFile':
            return self.handle_field_file(value, self.object)
        elif callable(value):
            return value()
        
    def handle_user(self, user):
        return user.get_full_name()
    
    def get_applicants_names(self, applicants):
        applicant_names = [applicant.get_full_name() for applicant in applicants.all()]
        return self.create_unordered_html_list(applicant_names)
    
    def get_object_list(self, object):
        list_of_objects = [obj for obj in object.all()]
        return self.create_unordered_html_list(list_of_objects)
    
    def create_unordered_html_list(self, list):
        html_output = mark_safe('<ul class="p-0">')

        for item in list:
            html_output += format_html('{}{}{}',
                mark_safe('<li>'),
                item,
                mark_safe('</li>')                
            )
        
        html_output += mark_safe('</ul>')

        return html_output
    
    def handle_field_file(self, field_file, object):
        from ..models import Proposal
        if type(object) == Proposal:
            if object.wmo.metc_decision_pdf and not object.is_practice():
                output = format_html('{}{}{}{}{}',
                                    mark_safe('<a href="'),
                                    f'{settings.BASE_URL}{field_file.url()}',
                                    mark_safe('" target="_blank">'),
                                    _('Download'),
                                    mark_safe('</a>')
                                    )
            else:
                output = _('Niet aangeleverd')
        else:
            #if obj == Observation
            output = format_html('{}{}{}{}{}',
                                    mark_safe('<a href="'),
                                    f'{settings.BASE_URL}{field_file.url()}',
                                    mark_safe('" target="_blank">'),
                                    _('Download'),
                                    mark_safe('</a>')
                                    )
        return output

def generate_pdf(proposal, template=False):
    """Grandfathered function for pdf saving. The template arg currently
    only exists for backwards compatibility."""

    from proposals.views.proposal_views import ProposalAsPdf

    view = ProposalAsPdf()
    view.object = proposal

    # Note, this is where the _view_ decides what kind of proposal it is
    # and chooses the appropriate template.
    context = view.get_context_data()

    with BytesIO() as f:
        view.get_pdf_response(
            context,
            dest=f,
        )
        pdf = ContentFile(f.getvalue())
    proposal.pdf.save(view.get_pdf_filename(), pdf)

    return proposal.pdf



def pdf_link_callback(uri, rel):
    """
    Convert HTML URIs to absolute system paths so xhtml2pdf can access those
    resources

    Retrieved from xhtml2pdf docs
    """
    result = finders.find(uri)
    if result:
        if not isinstance(result, (list, tuple)):
            result = [result]
        result = list(os.path.realpath(path) for path in result)
        path=result[0]
    else:
        sUrl = settings.STATIC_URL        # Typically /static/
        sRoot = settings.STATIC_ROOT      # Typically /home/userX/project_static/
        mUrl = settings.MEDIA_URL         # Typically /media/
        mRoot = settings.MEDIA_ROOT       # Typically /home/userX/project_static/media/

        if uri.startswith(mUrl):
            path = os.path.join(mRoot, uri.replace(mUrl, ""))
        elif uri.startswith(sUrl):
            path = os.path.join(sRoot, uri.replace(sUrl, ""))
        else:
            return uri

    # make sure that file exists
    if not os.path.isfile(path):
        raise Exception(
            'media URI must start with %s or %s' % (sUrl, mUrl)
        )
    return path


def check_local_facilities(proposal):
    """
    Checks whether local lab facilities are used in the given Proposal
    :param proposal: the current Proposal
    :return: an empty dictionary if no local support is needed, a dictionary with local facilities otherwise
    """
    result = defaultdict(set)

    def add_to_result(model):
        result[model._meta.verbose_name].add(model.description)

    for study in proposal.study_set.all():
        for recruitment in study.recruitment.all():
            if recruitment.is_local:
                add_to_result(recruitment)

        if study.has_intervention:
            for setting in study.intervention.setting.all():
                if setting.is_local:
                    add_to_result(setting)
        if study.has_observation:
            for setting in study.observation.setting.all():
                if setting.is_local:
                    add_to_result(setting)
        if study.has_sessions:
            for session in study.session_set.all():
                for setting in session.setting.all():
                    if setting.is_local:
                        add_to_result(setting)

                for task in session.task_set.all():
                    for registration in task.registrations.all():
                        if registration.is_local:
                            add_to_result(registration)

    return result


def notify_local_staff(proposal):
    """
    Notifies local lab staff of the current Proposal via e-mail.
    :param proposal: the current Proposal
    """
    # Change language to Dutch for this e-mail, but save the current language to reset it later
    current_language = get_language()
    activate('nl')

    secretary = get_secretary()

    if proposal.is_revision:
        subject = _('FETC-GW: gereviseerde aanvraag gebruikt labfaciliteiten')
    else:
        subject = _('FETC-GW: nieuwe aanvraag gebruikt labfaciliteiten')

    params = {
        'secretary': secretary.get_full_name(),
        'proposal': proposal,
        'applicants': [applicant.get_full_name() for applicant in proposal.applicants.all()],
        'facilities': sorted(check_local_facilities(proposal).items()),
        'is_revision': proposal.is_revision,
    }
    msg_plain = render_to_string('mail/local_staff_notify.txt', params)
    send_mail(subject, msg_plain, settings.EMAIL_FROM, [settings.EMAIL_LOCAL_STAFF])

    # Reset the current language
    activate(current_language)


@deconstructible
class FilenameFactory:
    '''A callable class which can be passed to upload_to() in FileFields
    and can be deconstructed for migrations'''

    def __init__(self, document_type):

        # document_type is a string describing the document kind,
        # such as "Informed_Consent"
        self.document_type = document_type

    def __call__(self, instance, original_fn):
        '''Returns a custom filename preserving the original extension,
        something like "FETC-2020-002-01-Villeneuve-T2-Informed-Consent.pdf"'''

        # Importing here to prevent circular import
        from proposals.models import Proposal, Wmo

        if isinstance(instance, Proposal):
            # This is a proposal PDF
            proposal = instance
            trajectory = None
        elif isinstance(instance, Wmo):
            # This is an METC decision file
            proposal = instance.proposal
            trajectory = None
        else:
            # In case of Documents objects
            proposal = instance.proposal
            try:
                trajectory = 'T' + str(instance.study.order)
            except AttributeError:
                # No associated study, so this is an extra Documents instance
                # We need to give it an index so they don't overwrite each other
                extra_index = 1

                # Again, to prevent circular imports
                from studies.models import Documents
                qs = Documents.objects.filter(
                    proposal=proposal).filter(
                        study=None)

                for docs in qs:
                    # The current Documents instance might not yet be saved and
                    # therefore not exist in the QS. Hence the for loop instead of
                    # the more traditional while
                    if docs == instance:
                        break # i.e. this may never happen
                    extra_index += 1

                # Unknown
                trajectory = 'Extra' + str(extra_index)

        chamber = proposal.reviewing_committee.name
        lastname = proposal.created_by.last_name
        refnum = proposal.reference_number

        extension = '.' + original_fn.split('.')[-1][-7:] # At most 7 chars seems reasonable

        fn_parts = ['FETC',
                    chamber,
                    refnum,
                    lastname,
                    trajectory,
                    self.document_type,
                    ]

        def not_empty(item):
            if item == None:
                return False
            if str(item) == '':
                return False
            return True

        # Translations will trip up join(), so we convert them here
        fn_parts = [str(p) for p in filter(not_empty, fn_parts)]

        return '-'.join(fn_parts) + extension


class OverwriteStorage(FileSystemStorage):

    def get_available_name(self, name, **kwargs):
        """Returns a filename that's free on the target storage system, and
        available for new content to be written to.

        Modified from http://djangosnippets.org/snippets/976/
        """
        import os

        # If the filename already exists, remove it
        if self.exists(name):
            os.remove(os.path.join(settings.MEDIA_ROOT, name))
        return super(OverwriteStorage, self).get_available_name(name, **kwargs)
