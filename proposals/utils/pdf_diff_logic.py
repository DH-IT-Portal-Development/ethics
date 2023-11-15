from datetime import date
from copy import copy

from django.conf import settings
from django.contrib.auth import get_user_model
from django.template.loader import get_template
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

from proposals.templatetags.proposal_filters import (
    needs_details,
    medical_traits,
    necessity_required,
    has_adults,
)
from proposals.templatetags.diff_tags import zip_equalize_lists


class BaseSection:
    """This is the main class, from which sections are constructed.
    It receives one object, such as a proposal or sub-objects of proposals.
    The most important methods are render and make_rows. Make rows makes use of get_row_field,
    which gets overwritten for specific sections, if logic is involved.
    For certain sections, there can be a sub-title, such as for studies or other cases.
    These are produced in the get_sub_title method and require a specific string, based on
    the type of sub-title required. The options are:
    - 'study'
    - 'session'
    - 'task'
    -'task_overview'
    These arguments are passed in overwritten __init__() methods, when applicable.
    """

    section_title = None
    row_fields = None

    def __init__(self, obj):
        self.obj = obj
        self.sub_title = None

    def make_rows(self):
        rows = [self.make_row_for_field(field) for field in self.get_row_fields()]
        return rows
    
    def make_row_for_field(self, field):
        if field in self.get_row_fields():
            return Row(self.obj, field)
        else:
            return None

    def get_row_fields(self):
        return self.row_fields

    def render(self, context):
        context = context.flatten()
        template = get_template("proposals/table_with_header.html")
        if self.sub_title is not None:
            context.update(
                {
                    "sub_title": self.sub_title,
                }
            )
        context.update(
            {
                "section_title": self.section_title,
                "rows": self.make_rows(),
            }
        )
        return template.render(context)

    def get_sub_title(self, obj, sub_title_type):
        return SubTitle(obj, sub_title_type).sub_title


class DiffSection:
    """For the diff page, sections are constructed by comparing two section objects.
    for instance:
          GeneralSection(old_proposal), GeneralSection(new_proposal)

    It mostly uses the make_rows methods, but also some other class variables from these objects.
    If a section is missing from a revision or an original proposal, this will be reperesented by
    None, and a warning and some formatting info get passed to the template as well.

    Some parts of this were written with the idea of allowing more than two objects to be compared,
    however, I did not end up pursuing this idea until the end."""

    def __init__(self, old_section, new_section):
        self.old_section = old_section
        self.new_section = new_section
        if self.old_section is None:
            self.warning = _(
                "Dit onderdeel is nieuw in de revisie en bestond niet in de originele aanvraag."
            )
            self.missing_object = "old"
            self.sub_title = self.new_section.sub_title
            self.section_title = self.new_section.section_title
        elif self.new_section is None:
            self.warning = _(
                "Dit onderdeel bestond in de originele aanvraag, maar niet meer in de revisie."
            )
            self.missing_object = "new"
            self.sub_title = self.old_section.sub_title
            self.section_title = self.old_section.section_title
        else:
            self.warning = None
            self.missing_object = None
            self.sub_title = self.old_section.sub_title
            self.section_title = self.old_section.section_title
        self.rows = self.make_diff_rows()

    def make_diff_rows(self):
        """This function generates rows for diff instances."""

        if self.missing_object is not None:
            # If there is a missing object, the template can just use the make_rows function
            # of the object that is not missing.
            if self.missing_object == "old":
                rows = self.new_section.make_rows()
            else:
                rows = self.old_section.make_rows()
            return rows
        else:
            all_fields = self.old_section.row_fields

            rows = []

            old_rows = self.old_section.make_rows()
            new_rows = self.new_section.make_rows()

            old_section_dict = {row.field: row for row in old_rows}
            new_section_dict = {row.field: row for row in new_rows}

            for field in all_fields:
                #If a field does not appear in either section, no row will be created.
                if field in old_section_dict and field in new_section_dict:
                    rows.append({'verbose_name':old_section_dict[field].verbose_name,
                                 'old_value': old_section_dict[field].value, 
                                 'new_value': new_section_dict[field].value}
                    )
                elif field in old_section_dict and not field in new_section_dict:
                    rows.append({'verbose_name':old_section_dict[field].verbose_name,
                                 'old_value': old_section_dict[field].value, 
                                 'new_value': ''}
                    )  
                elif field in new_section_dict and not field in old_section_dict:
                    rows.append({'verbose_name':new_section_dict[field].verbose_name,
                                 'old_value': '', 
                                 'new_value': new_section_dict[field].value}
                    )
                                    
            return rows

    def render(self, context):
        context = context.flatten()
        template = get_template("proposals/table_with_header_diff.html")

        if self.warning is not None:
            context.update(
                {
                    "warning": self.warning,
                    "missing_object": self.missing_object,
                }
            )
        if self.sub_title is not None:
            context.update(
                {
                    "sub_title": self.sub_title,
                }
            )
        context.update(
            {
                "section_title": self.section_title,
                "rows": self.rows,
            }
        )
        return template.render(context)

class Row:
    """This class creates rows for one objects, and gets initated
    in the make_rows method of Section classes. The classmethods of Rowclass
    are called in the templates of the render method of the PDF class, as well as in
    the make_diff_rows() method of the DiffSection"""

    verbose_name_diff_field_dict = {
        "get_metc_display": "metc",
        "get_is_medical_display": "is_medical",
    }

    def __init__(self, obj, field):
        self.obj = obj
        self.field = field

    def value(self):
        return RowValue(self.obj, self.field).get_field_value()
    
    def verbose_name(self):
        if self.field in self.verbose_name_diff_field_dict:
            verbose_name_field = self.verbose_name_diff_field_dict[self.field]
            verbose_name = self.get_verbose_name(verbose_name_field)
        else:
            verbose_name = self.get_verbose_name(self.field)
        return verbose_name

    def get_verbose_name(self, field):
        if field != "tasks_duration":
            return mark_safe(self.obj._meta.get_field(field).verbose_name)
        else:
            return mark_safe(
                self.obj._meta.get_field(field).verbose_name
                % self.obj.net_duration()
            )    

class RowValue:
    """The RowValue class manages the values of fields and correctly retrieves and/or formats
    the right values per field. This class get initiated in the value method
    of the Row class. It returns mostly strings, but sometimes some html as well."""

    def __init__(self, obj, field):
        self.obj = obj
        self.field = field

    def get_field_value(self):
        from ..models import Relation
        from studies.models import Compensation

        value = getattr(self.obj, self.field)

        User = get_user_model()

        if value in ("Y", "N", "?"):
            return self.yes_no_doubt(value)
        elif isinstance(value, bool):
            return _("ja") if value else _("nee")
        elif isinstance(value, (str, int, date)):
            return value
        elif value is None:
            return _("Onbekend")
        elif isinstance(value, User):
            return self.handle_user(value)
        elif isinstance(value, Relation) or isinstance(value, Compensation):
            return value.description
        elif value.__class__.__name__ == "ManyRelatedManager":
            if value.all().model == User:
                return self.get_applicants_names(value)
            else:
                return self.get_object_list(value)
        elif value.__class__.__name__ == "FieldFile":
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

    def create_unordered_html_list(self, lst):
        html_output = mark_safe('<p class="p-0">')

        for index, item in enumerate(lst):
            html_output += format_html("- {}", item)
            if index != len(lst) - 1:
                html_output += mark_safe('<br/>')

        html_output += mark_safe("</p>")

        return html_output

    def handle_field_file(self, field_file):
        if field_file:
            output = format_html(
                "<a href=https://{}>{}</a>",
                f"{settings.BASE_URL}{field_file.url}",
                _("Download"),
            )
        else:
            output = _("Niet aangeleverd")

        return output

    def yes_no_doubt(self, value):
        from main.models import YES_NO_DOUBT

        d = dict(YES_NO_DOUBT)
        return d[value]


class SubTitle:
    """This class can return a sub title to the base section class,
    according to the argument with which it is initiated. This argument gets passed
    in overwritten __init__ methods of for instance, the StudySection class."""

    def __init__(self, object, sub_title_type):
        if sub_title_type == "study":
            self.sub_title = self.get_study_title(object)
        elif sub_title_type == "session":
            self.sub_title = self.get_session_title(object)
        elif sub_title_type == "task":
            self.sub_title = self.get_task_title(object)
        elif sub_title_type == "task_overview":
            self.sub_title = _("Overzicht van het takenonderzoek")
        else:
            self.sub_title = None

    def get_study_title(self, study):
        from studies.models import Study

        if not isinstance(study, Study):
            study = study.study
        if study.proposal.studies_number > 1:
            if study.name:
                study_title = format_html(
                    "{}{} <em>{} </em>",
                    _("Traject "),
                    study.order,
                    study.name,
                )
            else:
                study_title = format_html(
                    "{}{}",
                    _("Traject"),
                    {study.order},
                )
        else:
            study_title = None
        return study_title

    def get_session_title(self, session):
        if session is None:
            return ""
        else:
            order = session.order
            study_order = session.study.order
            study_name = session.study.name
            studies_number = session.study.proposal.studies_number
            sessions_number = session.study.sessions_number

            if studies_number > 1 and sessions_number > 1:
                session_title = format_html(
                    "{}{} <em>{} </em> {}{}",
                    _("Traject "),
                    study_order,
                    study_name,
                    _("sessie "),
                    order,
                )
            elif studies_number > 1:
                session_title = format_html(
                    "{}{} <em>{} </em>",
                    _("Traject "),
                    study_order,
                    study_name,
                )
            elif sessions_number >= 1:
                session_title = format_html(
                    "{}{}",
                    _("Sessie "),
                    order,
                )
            return session_title

    def get_task_title(self, task):
        if task is None:
            return ""
        else:
            order = task.order
            session_order = task.session.order
            study_order = task.session.study.order
            study_name = task.session.study.name
            studies_number = task.session.study.proposal.studies_number
            if studies_number > 1:
                task_title = format_html(
                    "{}{} <em>{} </em>, {}{}{}{}",
                    _("Traject "),
                    study_order,
                    study_name,
                    _("sessie "),
                    session_order,
                    _(", taak "),
                    order,
                )
            else:
                task_title = format_html(
                    "{}{}{}{}",
                    _("Sessie "),
                    session_order,
                    _(", taak "),
                    order,
                )
            return task_title


class PageBreakMixin(BaseSection):
    """A Mixin for adding page break formatting to a section."""

    def render(self, context):
        context.update(
            {
                "page_break": True,
            }
        )
        return super().render(context)


class GeneralSection(BaseSection):
    """This class generates the data for the general section of a proposal and showcases
    the general workflow for creating sections. All possible row fields are provided, and
    removed according to the logic in the get_row_fields method.
    This class receives a proposal object.
    """

    section_title = _("Algemene informatie over de aanvraag")
    row_fields = [
        "is_pre_approved",
        "relation",
        "supervisor",
        "student_program",
        "student_context",
        "student_context_details",
        "student_justification",
        "other_applicants",
        "applicants",
        "other_stakeholders",
        "stakeholders",
        "date_start",
        "title",
        "funding",
        "funding_details",
        "funding_name",
        "pre_approval_institute",
        "pre_approval_pdf",
        "pre_assessment_pdf",
        "self_assessment",
        "summary",
    ]

    def get_row_fields(self):
        rows = copy(self.row_fields)
        obj = self.obj

        if not obj.is_pre_approved:
            rows.remove("is_pre_approved")
            rows.remove("pre_approval_institute")
            rows.remove("pre_approval_pdf")

        if obj.is_pre_assessment:
            rows.remove("funding")
            rows.remove("funding_name")
            rows.remove("funding_details")
            rows.remove("summary")
        else:
            rows.remove("pre_assessment_pdf")
            if not needs_details(obj.funding.all()):
                rows.remove("funding_details")
            if not needs_details(obj.funding.all(), "needs_name"):
                rows.remove("funding_name")

        if not obj.relation.needs_supervisor:
            rows.remove("supervisor")
        if not obj.relation.check_in_course:
            rows.remove("student_program")
            rows.remove("student_context")
            if obj.student_context is not None:
                if not obj.student_context.needs_details:
                    rows.remove("student_context_details")
            else:
                rows.remove("student_context_details")
            rows.remove("student_justification")
        if not obj.other_applicants:
            rows.remove("applicants")
        if not obj.other_stakeholders:
            rows.remove("stakeholders")

        return rows


class WMOSection(PageBreakMixin, BaseSection):
    """This class receives a proposal.wmo object."""

    section_title = _(
        "Ethische toetsing nodig door een Medische Ethische Toetsingscommissie (METC)?"
    )
    row_fields = [
        "get_metc_display",
        "metc_details",
        "metc_institution",
        "get_is_medical_display",
    ]

    def get_row_fields(self):
        rows = copy(self.row_fields)
        obj = self.obj

        if not obj.metc == "Y":
            rows.remove("metc_details")
            rows.remove("metc_institution")
        else:
            rows.remove("get_is_medical_display")

        return rows


class METCSection(PageBreakMixin, BaseSection):
    """This class receives a proposal.wmo object."""

    section_title = _("Aanmelding bij de METC")

    row_fields = ["metc_application", "metc_decision", "metc_decision_pdf"]


class TrajectoriesSection(PageBreakMixin, BaseSection):
    """This class receives a proposal object."""

    section_title = _("Eén of meerdere trajecten?")

    row_fields = ["studies_similar", "studies_number"]

    def get_row_fields(self):
        rows = copy(self.row_fields)
        obj = self.obj

        if obj.studies_similar:
            rows.remove("studies_number")

        return rows


class StudySection(PageBreakMixin, BaseSection):
    """This class receives a proposal.study object
    Note the overwritten __init__ method for adding a sub_title."""

    section_title = _("De deelnemers")
    row_fields = [
        "age_groups",
        "legally_incapable",
        "legally_incapable_details",
        "has_special_details",
        "special_details",
        "traits",
        "traits_details",
        "necessity",
        "necessity_reason",
        "recruitment",
        "recruitment_details",
        "compensation",
        "compensation_details",
        "hierarchy",
        "hierarchy_details",
    ]

    def __init__(self, obj):
        super().__init__(obj)
        self.sub_title = self.get_sub_title(self.obj, "study")

    def get_row_fields(self):
        rows = copy(self.row_fields)
        obj = self.obj

        if not has_adults(obj):
            rows.remove("legally_incapable")
            rows.remove("legally_incapable_details")
        elif not obj.legally_incapable:
            rows.remove("legally_incapable_details")
        if not obj.has_special_details:
            rows.remove("special_details")
            rows.remove("traits")
            rows.remove("traits_details")
        elif not medical_traits(obj.special_details.all()):
            rows.remove("traits")
            rows.remove("traits_details")
        elif not needs_details(obj.traits.all()):
            rows.remove("traits_details")
        if not necessity_required(obj):
            rows.remove("necessity")
            rows.remove("necessity_reason")
        if not needs_details(obj.recruitment.all()):
            rows.remove("recruitment_details")
        if not obj.compensation or not obj.compensation.needs_details:
            rows.remove("compensation_details")
        if not obj.hierarchy:
            rows.remove("hierarchy_details")

        return rows


class InterventionSection(BaseSection):
    """This class receives an intervention object"""

    section_title = _("Het interventieonderzoek")
    row_fields = [
        "setting",
        "setting_details",
        "supervision",
        "leader_has_coc",
        "period",
        "multiple_sessions",
        "session_frequency",
        "amount_per_week",
        "duration",
        "measurement",
        "experimenter",
        "description",
        "has_controls",
        "controls_description",
        "extra_task",
    ]

    def __init__(self, obj):
        super().__init__(obj)
        self.sub_title = self.get_sub_title(self.obj, "study")

    def get_row_fields(self):
        rows = copy(self.row_fields)
        obj = self.obj

        if obj.version == 1:
            fields_to_remove = ["multiple_sessions", "session_frequency", "extra_task"]
            for field in fields_to_remove:
                rows.remove(field)
        else:
            rows.remove("amount_per_week")
            if not obj.multiple_sessions:
                rows.remove("session_frequency")
            if obj.settings_contains_schools:
                rows.remove("extra_task")

        if not needs_details(obj.setting.all()):
            rows.remove("setting_details")
        if not obj.study.has_children() or not needs_details(
            obj.setting.all(), "needs_supervision"
        ):
            rows.remove("supervision")
            rows.remove("leader_has_coc")
        elif obj.supervision:
            rows.remove("leader_has_coc")
        if not obj.has_controls:
            rows.remove("controls_description")

        return rows


class ObservationSection(BaseSection):
    """This class receives an observation object"""

    section_title = _("Het observatieonderzoek")
    row_fields = [
        "setting",
        "setting_details",
        "supervision",
        "leader_has_coc",
        "days",
        "mean_hours",
        "details_who",
        "details_why",
        "details_frequency",
        "is_anonymous",
        "is_anonymous_details",
        "is_in_target_group",
        "is_in_target_group_details",
        "is_nonpublic_space",
        "is_nonpublic_space_details",
        "has_advanced_consent",
        "has_advanced_consent_details",
        "needs_approval",
        "approval_institution",
        "approval_document",
        "registrations",
        "registrations_details",
    ]

    def __init__(self, obj):
        super().__init__(obj)
        self.sub_title = self.get_sub_title(self.obj, "study")

    def get_row_fields(self):
        rows = copy(self.row_fields)
        obj = self.obj

        if obj.version == 1:
            to_remove_if_v1 = [
                "details_who",
                "details_why",
                "is_anonymous_details",
                "is_in_target_group_details",
                "is_nonpublic_space_details",
                "has_advanced_consent_details",
            ]
            for field in to_remove_if_v1:
                rows.remove(field)

            if not obj.is_nonpublic_space:
                rows.remove("has_advanced_consent")
            if not obj.needs_approval:
                rows.remove("approval_institution")
                rows.remove("approval_document")
            elif obj.study.proposal.is_practice():
                rows.remove("approval_document")
        else:
            to_remove_if_v2 = ["days", "mean_hours", "approval_document"]
            for field in to_remove_if_v2:
                rows.remove(field)

            if not obj.is_anonymous:
                rows.remove("is_anonymous_details")
            if not obj.is_in_target_group:
                rows.remove("is_in_target_group_details")
            if not obj.is_nonpublic_space:
                rows.remove("is_nonpublic_space_details")
                rows.remove("has_advanced_consent")
                rows.remove("has_advanced_consent_details")
            elif obj.has_advanced_consent:
                rows.remove("has_advanced_consent_details")
            if not needs_details(obj.setting.all(), "is_school"):
                rows.remove("needs_approval")
            if not obj.needs_approval:
                rows.remove("approval_institution")

        if not needs_details(obj.setting.all()):
            rows.remove("setting_details")
        if not obj.study.has_children() or not needs_details(
            obj.setting.all(), "needs_supervision"
        ):
            rows.remove("supervision")
            rows.remove("leader_has_coc")
        elif obj.supervision:
            rows.remove("leader_has_coc")
        if not needs_details(obj.registrations.all()):
            rows.remove("registrations_details")

        return rows


class SessionsOverviewSection(BaseSection):
    """This class receives an study object"""

    section_title = _("Het takenonderzoek en interviews")

    row_fields = ["sessions_number"]


class SessionSection(BaseSection):
    """This class receives a session object"""

    row_fields = [
        "setting",
        "setting_details",
        "supervision",
        "leader_has_coc",
        "tasks_number",
    ]

    def __init__(self, obj):
        super().__init__(obj)
        self.sub_title = self.get_sub_title(self.obj, "session")

    def get_row_fields(self):
        rows = copy(self.row_fields)
        obj = self.obj

        if not needs_details(obj.setting.all()):
            rows.remove("setting_details")
        if not obj.study.has_children() or not needs_details(
            obj.setting.all(), "needs_supervision"
        ):
            rows.remove("supervision")
            rows.remove("leader_has_coc")
        elif obj.supervision:
            rows.remove("leader_has_coc")

        return rows


class TaskSection(BaseSection):
    """This class receives a task object"""

    row_fields = [
        "name",
        "duration",
        "registrations",
        "registrations_details",
        "registration_kinds",
        "registration_kinds_details",
        "feedback",
        "feedback_details",
        "description",
    ]

    def __init__(self, obj):
        super().__init__(obj)
        self.sub_title = self.get_sub_title(self.obj, "task")

    def get_row_fields(self):
        rows = copy(self.row_fields)
        obj = self.obj

        if not needs_details(obj.registrations.all()):
            rows.remove("registrations_details")
        if not needs_details(
            obj.registrations.all(), "needs_kind"
        ) or not needs_details(obj.registration_kinds.all()):
            rows.remove("registration_kinds")
            rows.remove("registration_kinds_details")
        elif not needs_details(obj.registration_kinds.all()):
            rows.remove("registration_kinds_details")
        if not obj.feedback:
            rows.remove("feedback_details")

        return rows


class TasksOverviewSection(BaseSection):
    """Gets passed a session object"""

    row_fields = ["tasks_duration"]

    def __init__(self, obj):
        super().__init__(obj)
        self.sub_title = self.get_sub_title(self.obj, "task_overview")


class StudyOverviewSection(BaseSection):
    """This class receives a Study object."""

    section_title = _("Overzicht en eigen beoordeling van het gehele onderzoek")
    row_fields = [
        "deception",
        "deception_details",
        "negativity",
        "negativity_details",
        "stressful",
        "stressful_details",
        "risk",
        "risk_details",
    ]

    def __init__(self, obj):
        super().__init__(obj)
        self.sub_title = self.get_sub_title(self.obj, "study")

    def get_row_fields(self):
        rows = copy(self.row_fields)
        obj = self.obj

        rows_to_remove = []
        for x in range(0, 7, 2):
            if getattr(obj, rows[x]) == "N":
                rows_to_remove.append(rows[x + 1])
        rows = [row for row in rows if row not in rows_to_remove]

        if not obj.has_sessions and not obj.deception == "N":
            rows.remove("deception")
            rows.remove("deception_details")
        elif not obj.has_sessions:
            rows.remove("deception")

        return rows


class InformedConsentFormsSection(BaseSection):
    """This class receives a Documents object"""

    section_title = _("Informed consent formulieren")

    row_fields = [
        "translated_forms",
        "translated_forms_languages",
        "informed_consent",
        "briefing",
        "passive_consent",
        "passive_consent_details",
        "director_consent_declaration",
        "director_consent_information",
        "parents_information",
    ]

    def make_rows(self):
        """A few fields here need to access different objects, therefore this complex
        overriding of the make_rows function ... :("""

        proposal_list = ["translated_forms", "translated_forms_languages"]
        study_list = ["passive_consent", "passive_consent_details"]

        row_fields = self.get_row_fields()

        rows = []

        for field in row_fields:
            if field in proposal_list:
                rows.append(Row(self.obj.proposal, field))
            elif field in study_list:
                rows.append(Row(self.obj.study, field))
            else:
                rows.append(Row(self.obj, field))

        return rows

    def get_row_fields(self):
        rows = copy(self.row_fields)
        obj = self.obj

        if not obj.proposal.translated_forms:
            rows.remove("translated_forms_languages")
        if obj.proposal.is_practice() or not obj.informed_consent:
            rows.remove("informed_consent")
            rows.remove("briefing")
        if obj.study.passive_consent is None:
            rows.remove("passive_consent")
        if not obj.study.passive_consent:
            rows.remove("passive_consent_details")
        if not obj.director_consent_declaration:
            rows.remove("director_consent_declaration")
        if not obj.director_consent_information:
            rows.remove("director_consent_information")
        if not obj.parents_information:
            rows.remove("parents_information")

        return rows

class ExtraDocumentsSection(BaseSection):
    """This class receives an Documents object.
    Overrides the __init__ to create a formatted section title"""

    row_fields = [
        "informed_consent",
        "briefing",
        "director_consent_declaration",
        "director_consent_information",
        "parents_information",
    ]

    def __init__(self, obj, num):
        super().__init__(obj)
        self.section_title = _("Extra formulieren ") + str(num + 1)

    def get_row_fields(self):
        rows = copy(self.row_fields)
        obj = self.obj

        if not obj.informed_consent:
            rows.remove("informed_consent")
        if not obj.briefing:
            rows.remove("briefing")
        if not obj.director_consent_declaration:
            rows.remove("director_consent_declaration")
        if not obj.director_consent_information:
            rows.remove("director_consent_information")
        if not obj.parents_information:
            rows.remove("parents_information")

        return rows


class DMPFileSection(PageBreakMixin, BaseSection):
    """This class receives a proposal object
    Also unnecessary I suppose. But I though why not ..."""

    section_title = _("Data Management Plan")

    row_fields = ["dmp_file", "avg_understood"]


class EmbargoSection(BaseSection):
    """Gets passed a proposal object"""

    section_title = _("Aanmelding versturen")

    row_fields = ["embargo", "embargo_end_date"]

    def get_row_fields(self):
        rows = copy(self.row_fields)
        obj = self.obj

        if not obj.embargo:
            rows.remove("embargo_end_date")

        return rows


class CommentsSection(BaseSection):
    """Gets passed a proposal object. 
    """

    section_title = _("Ruimte voor eventuele opmerkingen")

    row_fields = ["comments"]


def get_extra_documents(obj):
    """A function to retrieve all extra documents for a specific proposal."""
    from studies.models import Documents

    extra_documents = []

    for document in Documents.objects.filter(proposal=obj, study__isnull=True):
        extra_documents.append(document)

    return extra_documents


def create_context_pdf(context, model):
    """A function to create the context for the PDF, which gets called in the ProposalAsPdf view."""

    sections = []

    sections.append(GeneralSection(model))

    if hasattr(model, 'wmo'):
        sections.append(WMOSection(model.wmo))

        if not model.is_pre_assessment:
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

                for num, document in enumerate(extra_documents):
                    sections.append(ExtraDocumentsSection(document, num))

                if model.dmp_file:
                    sections.append(DMPFileSection(model))

    sections.append(EmbargoSection(model))
    sections.append(CommentsSection(model))

    context["sections"] = sections

    return context


def multi_sections(section_type, objects, num=None):
    """A function that creates a list of sections of a specified type, from a list of
    objects, where it is possible for an object, such as a study, to be missing."""

    if num is None:
        return [section_type(obj) if obj is not None else None for obj in objects]
    else:
        return [section_type(obj, num) if obj is not None else None for obj in objects]


def get_all_related(objects, related_name):
    """Helper function for retrieving related objects"""

    return [
        getattr(obj, related_name, None) if obj is not None else None for obj in objects
    ]


def get_all_related_set(objects, related_name):
    """Helper function for retrieving a set of related objects."""

    return [
        getattr(obj, related_name, None).all() if obj is not None else None
        for obj in objects
    ]


def create_context_diff(context, old_proposal, new_proposal):
    """A function to create the context for the diff page."""

    sections = []

    sections.append(
        DiffSection(GeneralSection(old_proposal), GeneralSection(new_proposal))
    )

    if hasattr(new_proposal, 'wmo'):
        sections.append(
            DiffSection(WMOSection(old_proposal.wmo), WMOSection(new_proposal.wmo))
        )
        
        if new_proposal.is_pre_assessment:
            if (
                new_proposal.wmo.status != new_proposal.wmo.NO_WMO
                or old_proposal.wmo.status != old_proposal.wmo.NO_WMO
            ):
                sections.append(
                    DiffSection(METCSection(old_proposal.wmo), METCSection(new_proposal.wmo))
                )

            sections.append(
                DiffSection(
                    TrajectoriesSection(old_proposal), TrajectoriesSection(new_proposal)
                )
            )

            if (
                new_proposal.wmo.status == new_proposal.wmo.NO_WMO
                or new_proposal.wmo.status == new_proposal.wmo.JUDGED
            ):
                for old_study, new_study in zip_equalize_lists(
                    old_proposal.study_set.all(), new_proposal.study_set.all()
                ):
                    both_studies = [old_study, new_study]

                    sections.append(DiffSection(*multi_sections(StudySection, both_studies)))

                    if (
                        old_study is not None
                        and old_study.has_intervention
                        or new_study is not None
                        and new_study.has_intervention
                    ):
                        interventions = get_all_related(both_studies, "intervention")

                        sections.append(
                            DiffSection(*multi_sections(InterventionSection, interventions))
                        )

                    if (
                        old_study is not None
                        and old_study.has_observation
                        or new_study is not None
                        and new_study.has_observation
                    ):
                        observations = get_all_related(both_studies, "observation")

                        sections.append(
                            DiffSection(*multi_sections(ObservationSection, observations))
                        )

                    if (
                        old_study is not None
                        and old_study.has_sessions
                        or new_study is not None
                        and new_study.has_sessions
                    ):
                        sections.append(
                            DiffSection(*multi_sections(SessionsOverviewSection, both_studies))
                        )

                        old_sessions_set, new_sessions_set = get_all_related_set(
                            both_studies, "session_set"
                        )

                        for both_sessions in zip_equalize_lists(
                            old_sessions_set, new_sessions_set
                        ):
                            sections.append(
                                DiffSection(*multi_sections(SessionSection, both_sessions))
                            )

                            old_tasks_set, new_tasks_set = get_all_related_set(
                                both_sessions, "task_set"
                            )

                            for both_tasks in zip_equalize_lists(old_tasks_set, new_tasks_set):
                                sections.append(
                                    DiffSection(*multi_sections(TaskSection, both_tasks))
                                )

                        sections.append(
                            DiffSection(*multi_sections(TasksOverviewSection, both_sessions))
                        )

                    sections.append(
                        DiffSection(*multi_sections(StudyOverviewSection, both_studies))
                    )

                    both_documents = get_all_related(both_studies, "documents")

                    sections.append(
                        DiffSection(
                            *multi_sections(InformedConsentFormsSection, both_documents)
                        )
                    )

                old_extra_docs = get_extra_documents(old_proposal)
                new_extra_docs = get_extra_documents(new_proposal)

                if old_extra_docs or new_extra_docs:
                    for num, zipped_extra_docs in enumerate(
                        zip_equalize_lists(old_extra_docs, new_extra_docs)
                    ):
                        sections.append(
                            DiffSection(
                                *multi_sections(ExtraDocumentsSection, zipped_extra_docs, num)
                            )
                        )

                if old_proposal.dmp_file or new_proposal.dmp_file:
                    sections.append(
                        DiffSection(
                            *multi_sections(DMPFileSection, [old_proposal, new_proposal])
                        )
                    )

    sections.append(
        DiffSection(EmbargoSection(old_proposal), EmbargoSection(new_proposal))
    )
    sections.append(
        DiffSection(CommentsSection(old_proposal), CommentsSection(new_proposal))
    )

    context["sections"] = sections

    return context
