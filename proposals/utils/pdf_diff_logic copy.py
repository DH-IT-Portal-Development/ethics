
from datetime import date
from copy import copy

from django.conf import settings
from django.contrib.auth import get_user_model
from django.template.loader import get_template
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

from proposals.templatetags.proposal_filters import needs_details, medical_traits, \
necessity_required, has_adults
from proposals.templatetags.diff_tags import zip_equalize_lists

'''NOTE: As of now, the diff has no workaround for when observations or interventions are of a
different version, in the different proposals.'''

class BaseSection:

    section_title = None
    row_fields = None

    def make_rows(self):
        if self.object and self.object_2:
            row_fields_1 = self.get_row_fields(self.object)
            row_fields_2 = self.get_row_fields(self.object_2)

            row_fields_both = list(set(row_fields_1) | set(row_fields_2))

            #The merging above messes with the order, so I reorder it here
            row_fields = [row for row in self.row_fields if row in row_fields_both]

            rows = [RowClass(self.object, field, self.object_2) for field in row_fields]
        else:
            if self.object is None:
                obj = self.object_2
            else:
                obj = self.object          

            row_fields = self.get_row_fields(obj)

            rows = [RowClass(obj, field) for field in row_fields]
        return rows
    
    def get_row_fields(self, obj):
        return self.row_fields

class PDFDiffSection(BaseSection):
    '''This is the main class, from which most classes are constructed.
    It can take one object or two objects in a tuple, and produce html tables accordingly.
    The most important methods are render and make_rows. Make rows makes use of get_row_field,
    which is mostly overwritten for specific sections.
    If this class is used in the diff, object should be the parent object and object_2 the 
    revision/amendment.'''
    
    def __init__(self, object):
        if isinstance(object, tuple):
            self.object = object[0]
            self.object_2 = object[1]
        else:
            self.object = object
            self.object_2 = None

    def render(self, context):
        context = context.flatten()
        if self.object_2:
            template = get_template("proposals/table_with_header_diff.html")
        else:
            template = get_template("proposals/table_with_header.html")
        context.update(
            {
                "section_title": self.section_title,
                "rows": self.make_rows(),
            }
        )
        return template.render(context)

class DiffSectionMissingObjects(BaseSection):
    '''The DiffSectionMissingObjects class overrides the __init__ and render methods of the PDFDiffSection.
    This exists for instances of tables in the diff, where it is possible
    for objects to be entirely missing from one version or the other, such as studies.
    If neccesary, it provides an object is missing warning and some info for formatting the
    diff table. (self.missing_object)
    The resulting diff section class inherit from this class, plus their own section class.

    eg. class StudySectionDiff(DiffSectionMissingObjects, StudySection)'''

    def __init__(self, objects_tuple):
        if objects_tuple[0] is None:
            self.warning = _(
                "Dit onderdeel is nieuw in de revisie en bestond niet in de originele aanvraag."
                )
            self.missing_object = 0
        elif objects_tuple[1] is None:
            self.warning = _(
                "Dit onderdeel bestond in de originele aanvraag, maar niet meer in de revisie."
            )
            self.missing_object = 1
        else:
            self.warning = None
            self.missing_object = None
        self.object = objects_tuple[0]
        self.object_2 = objects_tuple[1]
    
    def render(self, context):
        context = context.flatten()
        template = get_template("proposals/table_with_header_diff.html")

        if self.warning is not None:
            context.update(
                {
                    "warning": self.warning,
                    "missing_object": self.missing_object
                }
            )
        context.update(
            {
                "section_title": self.section_title,
                "rows": self.make_rows(),
            }
        )
        return template.render(context)
class RowClass:
    '''This class creates rows for either one or two objects, and gets initated
    in the make_rows method of Section classes. The classmethods of Rowclass
    are called in the templates of the render method of the PDF class.'''

    verbose_name_diff_field_dict = {
        'get_metc_display': 'metc',
        'get_is_medical_display': 'is_medical'
    }

    def __init__(self, object, field, object_2 = None):
        self.object = object
        self.object_2 = object_2
        self.field = field
    
    def verbose_name(self):
        if self.field in self.verbose_name_diff_field_dict:
            verbose_name_field = self.verbose_name_diff_field_dict[self.field]
            verbose_name = self.get_verbose_name(verbose_name_field)
        else:
            verbose_name= self.get_verbose_name(self.field)
        return verbose_name   
    
    def value(self):
        return RowValueClass(self.object, self.field).get_field_value()
    
    def value_2(self):
        return RowValueClass(self.object_2, self.field).get_field_value()
    
    def get_verbose_name(self, field):
        if field != 'tasks_duration':
            return mark_safe(self.object._meta.get_field(field).verbose_name)
        else:
            return mark_safe(self.object._meta.get_field(field).verbose_name % self.object.net_duration())

class RowValueClass:
    '''The RowValueClass manages the values of fields and correctly retrieves and/or formats
    the right values per field. This class get initiated in the value and value_2 methods
    of the RowClass. It returns mostly strings, but sometimes some html as well.'''

    def __init__(self, object, field):

        self.object = object
        self.field = field

    def get_field_value(self):
        from ..models import Relation
        from studies.models import Compensation
        
        value = getattr(self.object, self.field)

        User = get_user_model()

        if value in ('Y', 'N', '?'):
            return self.yes_no_doubt(value)
        elif isinstance(value, bool):
            return _('ja') if value else _('nee')
        elif isinstance(value, (str, int, date)):
            return value
        elif value is None:
            return _('Onbekend')
        elif isinstance(value, User):
            return self.handle_user(value)
        elif isinstance(value, Relation) or isinstance(value, Compensation):
            return value.description
        elif value.__class__.__name__ == 'ManyRelatedManager':
            if value.all().model == User:
                return self.get_applicants_names(value)
            else:
                return self.get_object_list(value)
        elif value.__class__.__name__ == 'FieldFile':
            return self.handle_field_file(value)
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
            html_output += format_html('<li>{}</li>',
                item
            )
        
        html_output += mark_safe('</ul>')

        return html_output
    
    def handle_field_file(self, field_file):
        if field_file:
            output = format_html('<a href={}>{}</a>',
                f'{settings.BASE_URL}{field_file.url}',
                _('Download')
            )
        else:
            output = _('Niet aangeleverd')

        return output
    
    def yes_no_doubt(self, value):
        from main.models import YES_NO_DOUBT
        d = dict(YES_NO_DOUBT)
        return d[value]
    
class StudyTitleMixin:

    def get_study_title(self, study):
        if study.name:
            study_title = format_html('{}{} <em>{} </em>',
                                      _('Traject '),
                                      study.order,
                                      study.name
            )
        else:
            study_title = format_html('{}{}',
                                      _('Traject'),
                                      {study.order}
            )
        return study_title
    
    def get_session_title(self, session):
        if session is None:
            return ''
        else:
            order = session.order 
            study_order = session.study.order 
            study_name = session.study.name 
            studies_number = session.study.proposal.studies_number 
            sessions_number = session.study.sessions_number

            if studies_number > 1 and sessions_number > 1:
                session_title = format_html('{}{} <em>{} </em> {}{}',
                                        _('Traject '),
                                        study_order,
                                        study_name,
                                        _('sessie '),
                                        order
                )
            elif studies_number > 1:
                session_title = format_html('{}{} <em>{} </em>',
                                        _('Traject '),
                                        study_order,
                                        study_name,
                )
            elif sessions_number >= 1:
                session_title = format_html('{}{}',
                                            _('Sessie '),
                                            order
                )
            return session_title
    
    def get_task_title(self, task):
        if task is None:
            return ''
        else:
            order=task.order 
            session_order=task.session.order 
            study_order=task.session.study.order 
            study_name=task.session.study.name 
            studies_number=task.session.study.proposal.studies_number
            if studies_number > 1:
                task_title = format_html('{}{} <em>{} </em>, {}{}{}{}',
                                        _('Traject '),
                                        study_order,
                                        study_name,
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
        
def get_render_mixin(base, section):

    if section == 'study_title':
        class RenderStudyTitle(base, StudyTitleMixin):
            def render(self, context):
                '''Overriding the render function to pass study_title to the context.'''
                if self.object.proposal.studies_number > 1:
                    context.update(
                        {
                            'study_title': super().get_study_title(self.object)
                        }
                    )
                return super().render(context)
            
        return RenderStudyTitle
    
    elif section == 'sub_study_title':
        class RenderStudyTitle(base, StudyTitleMixin):

            def render(self, context):
                '''Overriding the render function to pass study_title to the context.'''
                if self.object.study.proposal.studies_number > 1:
                    context.update(
                        {
                            'study_title': super().get_study_title(self.object.study)
                        }
                    )
                return super().render(context)
            
        return RenderStudyTitle
    
    elif section == 'session_title':
        class RenderStudyTitle(base, StudyTitleMixin):

            def render(self, context):
                context.update(
                    {
                        'study_title': super().get_session_title(self.object)
                    }
                )
                return super().render(context)
            
        return RenderStudyTitle
    
    elif section == 'task_title':
        class RenderStudyTitle(base, StudyTitleMixin):

            def render(self, context):
                context.update(
                    {
                        'study_title': super().get_task_title(self.object)
                    }
                )
                return super().render(context)
            
        return RenderStudyTitle
    
    elif section == 'task_overview_title':
        class RenderStudyTitle(base, StudyTitleMixin):

            def render(self, context):
                context.update(
                    {
                        'study_title': _('Overzicht van het takenonderzoek')
                    }
                )
                return super().render(context)
                    
        return RenderStudyTitle
    

study_title = get_render_mixin(PDFDiffSection, 'study_title')
study_title_diff = get_render_mixin(DiffSectionMissingObjects, 'study_title')
sub_study_title = get_render_mixin(PDFDiffSection, 'sub_study_title')
sub_study_title_diff = get_render_mixin(DiffSectionMissingObjects, 'sub_study_title')
session_title = get_render_mixin(PDFDiffSection, 'session_title')
session_title_diff = get_render_mixin(DiffSectionMissingObjects, 'session_title')
task_title = get_render_mixin(PDFDiffSection, 'task_title')
task_title_diff = get_render_mixin(DiffSectionMissingObjects, 'task_title')
task_overview_title = get_render_mixin(PDFDiffSection, 'task_overview_title')
task_overview_title_diff = get_render_mixin(DiffSectionMissingObjects, 'task_overview_title')

class GeneralSection(PDFDiffSection):
    '''This class generates the data for the general section of a proposal and showcases
    the general workflow for creating sections. All possible row fields are provided, and
    removed according to the logic in the get_row_fields method.
    This class receives a proposal object.'''

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
        'summary'
    ]
    
    def get_row_fields(self, obj):
        rows = copy(self.row_fields)

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

        return rows
    
class PageBreakMixin(PDFDiffSection):

    def render(self, context):
        context.update(
            {
                'page_break': True
            }
        )
        return super().render(context)

    
class WMOSection(PageBreakMixin, PDFDiffSection):
    '''This class receives a proposal.wmo object.'''
    section_title = _("Ethische toetsing nodig door een Medische Ethische Toetsingscommissie (METC)?")
    row_fields = [
        'get_metc_display',
        'metc_details',
        'metc_institution',
        'get_is_medical_display',  
    ]
    
    def get_row_fields(self, obj):
        rows = copy(self.row_fields)

        if not obj.metc == 'Y':
            rows.remove('metc_details')
            rows.remove('metc_institution')
        else:
            rows.remove('get_is_medical_display')

        return rows
    
class METCSection(PageBreakMixin, PDFDiffSection):
    '''This class receives a proposal.wmo object.
    This class exists because the RowValueClass does some
    funky things for working with the metc_decision_pdf field'''
    section_title = _("Aanmelding bij de METC")
    
    row_fields = [
        'metc_application',
        'metc_decision',
        'metc_decision_pdf'
    ]
    
class TrajectoriesSection(PageBreakMixin, PDFDiffSection):
    '''This class receives a proposal object.'''

    section_title = _("Eén of meerdere trajecten?")

    row_fields = [
        'studies_similar',
        'studies_number'
    ]
    
    def get_row_fields(self, obj):
        rows = copy(self.row_fields)

        if obj.studies_similar:
            rows.remove('studies_number')

        return rows

class StudySection(study_title):
    '''This class receives a proposal.study object.'''
    section_title = _('De deelnemers')
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

    def get_row_fields(self, obj):
        rows = copy(self.row_fields)

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

        return rows
    
    
class StudySectionDiff(study_title_diff, StudySection):
    '''An example of a DiffSectionMissingObjects. Unfortunately I found myself having to repeat the overriding
    of the render function from the studySection, due to the mro.'''
    pass

class BaseInterventionSection(sub_study_title):

    section_title = _('Het interventieonderzoek')
    row_fields = [
        'setting',
        'setting_details',
        'supervision',
        'leader_has_coc',
        'period',
        'duration',
        'measurement',
        'experimenter',
        'description',
        'has_controls',
        'controls_description'
    ]

    def get_row_fields(self, obj):
        rows = copy(self.row_fields)
        
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

        return rows

class BaseInterventionSectionDiff(sub_study_title_diff, BaseInterventionSection):
    pass

class InterventionSectionV1(BaseInterventionSection):

    def __init__(self, object):
        super().__init__(object)
        self.row_fields = super().get_row_fields(object)
        self.row_fields[5:5] = ['multiple_sessions', 'session_frequency']
        self.row_fields.append('extra_task')
    
class InterventionSectionV1Diff(BaseInterventionSectionDiff, InterventionSectionV1):
    pass

class InterventionSection(sub_study_title):
    '''This class receives an intervention object'''
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

    def get_row_fields(self, obj):
        rows = copy(self.row_fields)

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

        return rows
    
class InterventionSectionDiff(sub_study_title_diff, InterventionSection):
    pass
    
class ObservationSection(sub_study_title):
    '''This class receives an observation object
    It inherits from the InterventionSection, as it can repurpose the same overridden
    render method.'''
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

    def get_row_fields(self, obj):
        rows = copy(self.row_fields)

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

        return rows
    
class ObservationSectionDiff(sub_study_title_diff, ObservationSection):
    '''Note that the diff sections follow a similar pattern of inheritance as 
    the regular sections, due to repurposing overriden methods, when applicable, 
    eg.:

    class InterventionSection(PDFDiffSection)
    class InterventionSectionDiff(DiffSectionMissingObjects, InterventionSection)

    class ObservationSection(InterventionSection)
    class ObservationSectionDiff(InterventionSectionDiff, ObservationSection)
    '''
    pass

class SessionsOverviewSection(study_title):
    '''This class receives an study object
    This Section looks maybe a bit unnecessary, but it does remove some logic, plus
    the study_title.html from the template.'''

    section_title = _("Het takenonderzoek en interviews")

    row_fields = ['sessions_number']


class SessionsOverviewSectionDiff(study_title_diff, SessionsOverviewSection):
    '''Needed to override get_row_fields, due to mro issue'''
    pass

class SessionSection(session_title):
    '''This class receives a session object'''
    
    row_fields = [
        'setting',
        'setting_details',
        'supervision',
        'leader_has_coc',
        'tasks_number',       
    ]

    def get_row_fields(self, obj):
        rows = copy(self.row_fields)

        if not needs_details(obj.setting.all()):
            rows.remove('setting_details')
        if not obj.study.has_children() or \
        not needs_details(obj.setting.all(), 'needs_supervision'):
            rows.remove('supervision')
            rows.remove('leader_has_coc')
        elif obj.supervision:
            rows.remove('leader_has_coc')

        return rows

class SessionSectionDiff(session_title_diff, SessionSection):
    pass
    
class TaskSection(task_title):
    '''This class receives an task object'''
    
    row_fields = [
        'name',
        'duration',
        'registrations',
        'registrations_details',
        'registration_kinds',
        'registration_kinds_details',
        'feedback',
        'feedback_details',
        'description'
    ]

    def get_row_fields(self, obj):
        rows = copy(self.row_fields)

        if not needs_details(obj.registrations.all()):
            rows.remove('registrations_details')
        if not needs_details(obj.registrations.all(), 'needs_kind') or \
        not needs_details(obj.registration_kinds.all()):
            rows.remove('registration_kinds')
            rows.remove('registration_kinds_details')
        elif not needs_details(obj.registration_kinds.all()):
            rows.remove('registration_kinds_details')
        if not obj.feedback:
            rows.remove('feedback_details')

        return rows
    
class TaskSectionDiff(task_title_diff, TaskSection):
    pass
    
class TasksOverviewSection(task_overview_title):
    '''Gets passed a session object
    This might be unecessary ... Maybe just use the existing template language ...
    Because the verbose name of this field is formatted, the method for retrieving
    the verbose name in the RowClass is quite convoluded.'''

    row_fields = [
        'tasks_duration'
    ]
    
class TasksOverviewSectionDiff(task_overview_title_diff, TasksOverviewSection):
    pass
    
class StudyOverviewSection(study_title):
    '''This class receives a Study object.'''

    section_title = _('Overzicht en eigen beoordeling van het gehele onderzoek')
    row_fields = [
        'deception',
        'deception_details',
        'negativity',
        'negativity_details',
        'stressful',
        'stressful_details',
        'risk',
        'risk_details'
    ]

    def get_row_fields(self, obj):
        rows = copy(self.row_fields)

        rows_to_remove = []
        for x in range(0, 7, 2):
            if getattr(obj, rows[x]) == 'N':
                rows_to_remove.append(rows[x+1])
        rows = [row for row in rows if row not in rows_to_remove]

        if not obj.has_sessions and not obj.deception == 'N':
            rows.remove('deception')
            rows.remove('deception_details')
        elif not obj.has_sessions:
            rows.remove('deception')

        return rows

class StudyOverviewSectionDiff(study_title_diff, StudyOverviewSection):
    pass
    
class InformedConsentFormsSection(sub_study_title):
    '''This class receives a Documents object'''

    section_title = _('Informed consent formulieren')

    row_fields = [
        'translated_forms',
        'translated_forms_languages',
        'informed_consent',
        'briefing',
        'passive_consent',
        'passive_consent_details',
        'director_consent_declaration',
        'director_consent_information',
        'parents_information'
    ]

    def make_rows(self):

        '''A few fields here need to access different objects, therefore this complex
        overriding of the make_rows function ... :( '''

        proposal_list = ['translated_forms', 'translated_forms_languages']
        study_list = ['passive_consent', 'passive_consent_details']
        if self.object_2:
            row_fields_1 = self.get_row_fields(self.object)
            row_fields_2 = self.get_row_fields(self.object_2)

            row_fields_both = list(set(row_fields_1) | set(row_fields_2))

            ordered_row_fields = [row for row in self.row_fields if row in row_fields_both]

            rows = []

            for field in ordered_row_fields:
                if field in proposal_list:
                    rows.append(RowClass(self.object.proposal, field, self.object_2.proposal))
                elif field in study_list:
                    rows.append(RowClass(self.object.study, field, self.object_2.study))
                else:
                    rows.append(RowClass(self.object, field, self.object_2))
                    
        else:
            row_fields = self.get_row_fields(self.object)

            rows = []

            for field in row_fields:
                if field in proposal_list:
                    rows.append(RowClass(self.object.proposal, field))
                elif field in study_list:
                    rows.append(RowClass(self.object.study, field))
                else:
                    rows.append(RowClass(self.object, field))
    
        return rows
    
    def get_row_fields(self, obj):
        rows = copy(self.row_fields)

        if not obj.proposal.translated_forms:
            rows.remove('translated_forms_languages')
        if obj.proposal.is_practice() or not obj.informed_consent:
            rows.remove('informed_consent')
            rows.remove('briefing')
        if obj.study.passive_consent is None:
            rows.remove('passive_consent')
        if not obj.study.passive_consent:
            rows.remove('passive_consent_details')
        if not obj.director_consent_declaration:
            rows.remove('director_consent_declaration')
        if not obj.director_consent_information:
            rows.remove('director_consent_information')
        if not obj.parents_information:
            rows.remove('parents_information')

        return rows
    
class InformedConsentSectionDiff(sub_study_title_diff, InformedConsentFormsSection):
    pass
    
class ExtraDocumentsSection(PDFDiffSection):
    '''This class receives an Documents object.
    Overrides the __init__ to create a formatted section title'''

    row_fields = [
        'informed_consent',
        'briefing'
    ]

    def __init__(self, object, count):
        super().__init__(object)
        self.section_title = _('Extra formulieren ') + str(count + 1)
    
    def get_row_fields(self, obj):
        rows = copy(self.row_fields)

        if not obj.informed_consent:
            rows.remove('informed_consent')
        if not obj.briefing:
            rows.remove('briefing')

        return rows
    
class ExtraDocumentsSectionDiff(DiffSectionMissingObjects, ExtraDocumentsSection):

    def __init__(self, objects_tuple, count):
        super().__init__(objects_tuple)
        self.section_title = _('Extra formulieren ') + str(count+1)     
    
class DMPFileSection(PDFDiffSection):
    '''This class receives a proposal object
    Also unnecessary I suppose. But I though why not ...'''

    section_title = _('Data Management Plan')
    
    row_fields = ['dmp_file']

class EmbargoSection(PDFDiffSection):
    '''Gets passed a proposal object'''

    section_title = _('Aanmelding versturen')

    row_fields = [
        'embargo',
        'embargo_end_date'
    ]

    def get_row_fields(self, obj):
        rows = copy(self.row_fields)

        if not obj.embargo:
            rows.remove('embargo_end_date')

        return rows
    
def get_extra_documents(object):
    '''A function to retrieve all extra documents for a specific proposal.'''
    from studies.models import Documents

    extra_documents = []

    for document in Documents.objects.filter(
        proposal = object,
        study__isnull = True
    ):
        extra_documents.append(document)
    
    return extra_documents
    
def create_context_pdf(context, model):
    '''A function to create the context for the PDF.'''

    sections = []

    sections.append(GeneralSection(model))
    sections.append(WMOSection(model.wmo))

    if model.wmo.status != model.wmo.NO_WMO:
        sections.append(METCSection(model.wmo))
    
    sections.append(TrajectoriesSection(model))

    if model.wmo.status == model.wmo.NO_WMO:

        for study in model.study_set.all():
            sections.append(StudySection(study))
            if study.has_intervention:
                sections.append(InterventionSection(study.intervention))
            if study.has_observation:
                sections.append(ObservationSection(study.observation))
            if study.has_sessions:
                sections.append(SessionsOverviewSection(study))
                for session in study.session_set.all():
                    sections.append(SessionSection(session))
                    for task in session.task_set.all():
                        sections.append(TaskSection(task))
                sections.append(TasksOverviewSection(session))
            sections.append(StudyOverviewSection(study))
            sections.append(InformedConsentFormsSection(study.documents))

        extra_documents = get_extra_documents(model)
        
        for count, document in enumerate(extra_documents):
            sections.append(ExtraDocumentsSection(document, count))

        if model.dmp_file:
            sections.append(DMPFileSection(model))
            
        sections.append(EmbargoSection(model))

    context['sections'] = sections
    
    return context

def create_context_diff(context, p_proposal, proposal):
    '''A function to create the context for the diff page.'''

    both_proposals = (p_proposal, proposal)

    sections = []

    sections.append(GeneralSection(both_proposals))
    sections.append(WMOSection((p_proposal.wmo, proposal.wmo)))

    if proposal.wmo.status != proposal.wmo.NO_WMO or p_proposal.wmo.status != p_proposal.wmo.NO_WMO:
        sections.append(METCSection((p_proposal.wmo, proposal.wmo)))
    
    sections.append(TrajectoriesSection(both_proposals))

    if proposal.wmo.status == proposal.wmo.NO_WMO or proposal.wmo.status == proposal.wmo.JUDGED:

        for p_study, study in zip_equalize_lists(p_proposal.study_set.all(), proposal.study_set.all()):

            diff_studies = (p_study, study)

            sections.append(StudySectionDiff((diff_studies)))

            if p_study is not None and p_study.has_intervention or \
                study is not None and study.has_intervention:


                interventions = tuple((study.intervention if study is not None \
                                       else study for study in diff_studies))
                
                sections.append(InterventionSectionDiff(interventions))

            if p_study is not None and p_study.has_observation or \
                study is not None and study.has_observation:

                observations = tuple((study.observation if study is not None \
                                       else study for study in diff_studies))
                
                sections.append(ObservationSectionDiff(observations))

            if p_study is not None and p_study.has_sessions or \
                study is not None and study.has_sessions:

                sections.append(SessionsOverviewSectionDiff(diff_studies))

                p_sessions_set, sessions_set = tuple((study.session_set.all() if study is not None \
                                       else study for study in diff_studies))
                
                for diff_sessions in zip_equalize_lists(p_sessions_set, sessions_set):

                    sections.append(SessionSectionDiff(diff_sessions))

                    p_tasks_set, tasks_set = tuple((session.task_set.all() if session is not None \
                                       else session for session in diff_sessions))
                    
                    for diff_tasks in zip_equalize_lists(p_tasks_set, tasks_set):

                        sections.append(TaskSectionDiff(diff_tasks))

                sections.append(TasksOverviewSectionDiff(diff_sessions))

            sections.append(StudyOverviewSectionDiff(diff_studies))

            documents = tuple(study.documents if study is not None \
                              else study for study in diff_studies)
            
            sections.append(InformedConsentSectionDiff(documents))

        p_extra_docs = get_extra_documents(p_proposal)
        extra_docs = get_extra_documents(proposal)

        if p_extra_docs or extra_docs:
            for count, zipped_extra_docs in enumerate(zip_equalize_lists(p_extra_docs, extra_docs)):
                sections.append(ExtraDocumentsSectionDiff(zipped_extra_docs, count))

        if p_proposal.dmp_file or proposal.dmp_file:
            sections.append(DMPFileSection(both_proposals))
            
        sections.append(EmbargoSection(both_proposals))

    context['sections'] = sections

    return context


