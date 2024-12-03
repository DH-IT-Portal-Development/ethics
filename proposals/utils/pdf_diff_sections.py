from datetime import date
from copy import copy

from django.utils.translation import gettext as _

from proposals.templatetags.proposal_filters import (
    needs_details,
    medical_traits,
    necessity_required,
    has_adults,
)
from proposals.utils.pdf_diff_utils import (
    BaseSection,
    Row,
    PageBreakMixin,
)

##############
# General info
##############


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


##############
# WMO sections
##############


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


################
# Study sections
################


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


class SessionSection(BaseSection):
    """This class receives a session object"""

    row_fields = [
        "repeats",
        "setting",
        "setting_details",
        "supervision",
        "leader_has_coc",
    ]

    def __init__(self, obj):
        super().__init__(obj)
        if self.obj.order == 1:
            self.section_title = _("Het takenonderzoek en interviews")
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
        "repeats",
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
        for x in range(0, len(self.row_fields), 2):
            if getattr(obj, rows[x]) == "N":
                rows_to_remove.append(rows[x + 1])
        rows = [row for row in rows if row not in rows_to_remove]

        if not obj.has_sessions and not obj.deception == "N":
            rows.remove("deception")
            rows.remove("deception_details")
        elif not obj.has_sessions:
            rows.remove("deception")

        return rows


class KnowledgeSecuritySection(BaseSection):
    """This class receives a Proposal object."""

    section_title = _("Kennisveiligheid en risico onderzoekers")
    row_fields = [
        "knowledge_security",
        "knowledge_security_details",
        "researcher_risk",
        "researcher_risk_details",
    ]

    def get_row_fields(self):
        rows = copy(self.row_fields)
        obj = self.obj

        rows_to_remove = []
        for x in range(0, len(self.row_fields), 2):
            if getattr(obj, rows[x]) == "N":
                rows_to_remove.append(rows[x + 1])
        rows = [row for row in rows if row not in rows_to_remove]

        return rows


######################
# Attachments Sections
######################


class TranslatedFormsSection(BaseSection):
    """This class receives a Proposal object"""

    section_title = _("Vertaling formulieren")

    row_fields = [
        "translated_forms",
        "translated_forms_languages",
    ]

    def get_row_fields(self):
        rows = copy(self.row_fields)
        obj = self.obj

        if not obj.translated_forms:
            rows.remove("translated_forms_languages")

        return rows


###############
# FinalSections
###############


class DMPFileSection(PageBreakMixin, BaseSection):
    """
    This class receives a proposal object
    NOTE: dmp_file is for legacy proposals, should be covered by new attachment
    system.
    """

    section_title = _("Data Management Plan")

    row_fields = ["dmp_file", "privacy_officer"]

    def get_row_fields(self):
        rows = copy(self.row_fields)
        obj = self.obj

        if not obj.dmp_file:
            rows.remove("dmp_file")

        return rows


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
    """Gets passed a proposal object."""

    section_title = _("Ruimte voor eventuele opmerkingen")

    row_fields = ["comments"]


########################
# Legacy Documents stuff
########################


class InformedConsentFormsSection(BaseSection):
    """This class receives a Documents object"""

    section_title = _("Informed consent formulieren")

    row_fields = [
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

        study_list = ["passive_consent", "passive_consent_details"]

        row_fields = self.get_row_fields()

        rows = []

        for field in row_fields:
            if field in study_list:
                rows.append(Row(self.obj.study, field))
            else:
                rows.append(Row(self.obj, field))

        return rows

    def get_row_fields(self):
        rows = copy(self.row_fields)
        obj = self.obj

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
