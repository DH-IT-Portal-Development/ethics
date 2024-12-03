from datetime import date
from copy import copy

from django.utils.translation import gettext as _

from proposals.templatetags.diff_tags import zip_equalize_lists
from proposals.templatetags.proposal_filters import (
    needs_details,
    medical_traits,
    necessity_required,
    has_adults,
)
from proposals.utils.pdf_diff_utils import (
    BaseSection,
    DiffSection,
    Row,
    PageBreakMixin,
    TitleSection,
    get_all_related,
    get_all_related_set,
    get_extra_documents,
    multi_sections,
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


class PersonalDataSection(BaseSection):
    """This class receives a proposal.study object
    Note the overwritten __init__ method for adding a sub_title."""

    section_title = _("Persoonlijke gegevens")
    row_fields = [
        "legal_basis",
        "has_special_details",
        "special_details",
        "traits",
        "traits_details",
    ]

    def __init__(self, obj):
        super().__init__(obj)
        self.sub_title = self.get_sub_title(self.obj, "study")

    def get_row_fields(self):
        rows = copy(self.row_fields)
        obj = self.obj

        if not obj.has_special_details:
            rows.remove("special_details")
            rows.remove("traits")
            rows.remove("traits_details")
        elif not medical_traits(obj.special_details.all()):
            rows.remove("traits")
            rows.remove("traits_details")
        elif not needs_details(obj.traits.all()):
            rows.remove("traits_details")

        return rows


class StudySection(PageBreakMixin, BaseSection):
    """This class receives a proposal.study object
    Note the overwritten __init__ method for adding a sub_title."""

    section_title = _("De deelnemers")
    row_fields = [
        "age_groups",
        "legally_incapable",
        "legally_incapable_details",
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
    
class AttachmentSection(BaseSection):

    section_title = ""

    row_fields = [
        "upload",
        "name",
        "comments",
    ]

    def __init__(self, obj, sub_title, proposal):
        super().__init__(obj)
        self.sub_title = sub_title
        self.proposal = proposal
    
    def make_row_for_field(self, field):
        if field in self.get_row_fields():
            return Row(self.obj, field, self.proposal)
        else:
            return None


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
    
##########################    
# Create the full PDF/diff
##########################

def create_attachment_sections(proposal):
    from proposals.utils.stepper import Stepper

    attachment_sections = []

    stepper = Stepper(proposal)
    slots = [slot for slot in stepper.attachment_slots if slot.attachment]

    objects = [proposal] + list(proposal.study_set.all())
    slot_dict = {obj: [] for obj in objects}
    for slot in slots:
        relevant_owner = slot.attachment.get_owner_for_proposal(proposal)
        slot_dict[relevant_owner].append(slot)
    
    for owner in slot_dict:
        if slot_dict[owner]:
            if owner == proposal:
                title = _("Aanvraag in het geheel")
            elif proposal.study_set.count() == 1:
                title = _("Het hoofdtraject")
            else:
                title = _("Traject ") + owner.order + ": " + owner.name
            attachment_sections.append(TitleSection(title))
            for slot in slot_dict[owner]:
                attachment_sections.append(AttachmentSection(slot.attachment, sub_title=slot.kind.name, proposal=slot.get_proposal()))

    return attachment_sections

def create_context_pdf(context, proposal):
    """A function to create the context for the PDF, which gets called in the ProposalAsPdf view."""
    from reviews.templatetags.documents_list import get_legacy_documents

    sections = []

    # Check if the proposal has legacy documents. Just used as a bool.
    has_legacy_docs = bool(get_legacy_documents(proposal))

    sections.append(GeneralSection(proposal))

    if hasattr(proposal, "wmo"):
        sections.append(WMOSection(proposal.wmo))

        if not proposal.is_pre_assessment:
            if proposal.wmo.status != proposal.wmo.WMOStatuses.NO_WMO:
                sections.append(METCSection(proposal.wmo))

            sections.append(TrajectoriesSection(proposal))

            if proposal.wmo.status == proposal.wmo.WMOStatuses.NO_WMO:
                for study in proposal.study_set.all():
                    sections.append(StudySection(study))
                    sections.append(PersonalDataSection(study))
                    if study.get_intervention():
                        sections.append(InterventionSection(study.intervention))
                    if study.get_observation():
                        sections.append(ObservationSection(study.observation))
                    if study.get_sessions():
                        for session in study.session_set.all():
                            sections.append(SessionSection(session))
                            for task in session.task_set.all():
                                sections.append(TaskSection(task))
                            sections.append(TasksOverviewSection(session))
                    sections.append(StudyOverviewSection(study))
                    if has_legacy_docs:
                        sections.append(InformedConsentFormsSection(study.documents))

                sections.append(KnowledgeSecuritySection(proposal))

                sections.extend(create_attachment_sections(proposal))

                sections.append(TranslatedFormsSection(proposal))

                if has_legacy_docs:

                    extra_documents = get_extra_documents(proposal)

                    for num, document in enumerate(extra_documents):
                        sections.append(ExtraDocumentsSection(document, num))

                sections.append(DMPFileSection(proposal))

    sections.append(EmbargoSection(proposal))
    sections.append(CommentsSection(proposal))

    context["sections"] = sections

    return context

def create_context_diff(context, old_proposal, new_proposal):
    """A function to create the context for the diff page."""
    from reviews.templatetags.documents_list import get_legacy_documents

    sections = []

    has_legacy_docs = get_legacy_documents(old_proposal) or get_legacy_documents(
        new_proposal
    )

    sections.append(
        DiffSection(GeneralSection(old_proposal), GeneralSection(new_proposal))
    )

    if hasattr(new_proposal, "wmo"):
        sections.append(
            DiffSection(WMOSection(old_proposal.wmo), WMOSection(new_proposal.wmo))
        )

        if not new_proposal.is_pre_assessment:
            if (
                new_proposal.wmo.status != new_proposal.wmo.WMOStatuses.NO_WMO
                or old_proposal.wmo.status != old_proposal.wmo.WMOStatuses.NO_WMO
            ):
                sections.append(
                    DiffSection(
                        METCSection(old_proposal.wmo), METCSection(new_proposal.wmo)
                    )
                )

            sections.append(
                DiffSection(
                    TrajectoriesSection(old_proposal), TrajectoriesSection(new_proposal)
                )
            )

            if (
                new_proposal.wmo.status == new_proposal.wmo.WMOStatuses.NO_WMO
                or new_proposal.wmo.status == new_proposal.wmo.WMOStatuses.JUDGED
            ):
                for old_study, new_study in zip_equalize_lists(
                    old_proposal.study_set.all(), new_proposal.study_set.all()
                ):
                    both_studies = [old_study, new_study]

                    sections.append(
                        DiffSection(*multi_sections(StudySection, both_studies))
                    )

                    sections.append(
                        DiffSection(*multi_sections(PersonalDataSection, both_studies))
                    )

                    if (
                        old_study is not None
                        and old_study.get_intervention()
                        or new_study is not None
                        and new_study.get_intervention()
                    ):
                        interventions = get_all_related(both_studies, "intervention")

                        sections.append(
                            DiffSection(
                                *multi_sections(InterventionSection, interventions)
                            )
                        )

                    if (
                        old_study is not None
                        and old_study.get_observation()
                        or new_study is not None
                        and new_study.get_observation()
                    ):
                        observations = get_all_related(both_studies, "observation")

                        sections.append(
                            DiffSection(
                                *multi_sections(ObservationSection, observations)
                            )
                        )

                    if (
                        old_study is not None
                        and old_study.get_sessions()
                        or new_study is not None
                        and new_study.get_sessions()
                    ):
                        old_sessions_set, new_sessions_set = get_all_related_set(
                            both_studies, "session_set"
                        )

                        for both_sessions in zip_equalize_lists(
                            old_sessions_set, new_sessions_set
                        ):
                            sections.append(
                                DiffSection(
                                    *multi_sections(SessionSection, both_sessions)
                                )
                            )

                            old_tasks_set, new_tasks_set = get_all_related_set(
                                both_sessions, "task_set"
                            )

                            for both_tasks in zip_equalize_lists(
                                old_tasks_set, new_tasks_set
                            ):
                                sections.append(
                                    DiffSection(
                                        *multi_sections(TaskSection, both_tasks)
                                    )
                                )

                            sections.append(
                                DiffSection(
                                    *multi_sections(TasksOverviewSection, both_sessions)
                                )
                            )

                    sections.append(
                        DiffSection(*multi_sections(StudyOverviewSection, both_studies))
                    )

                    if has_legacy_docs:
                        both_documents = get_all_related(both_studies, "documents")

                        sections.append(
                            DiffSection(
                                *multi_sections(
                                    InformedConsentFormsSection, both_documents
                                )
                            )
                        )

                sections.append(
                    DiffSection(
                        KnowledgeSecuritySection(old_proposal),
                        KnowledgeSecuritySection(new_proposal),
                    )
                )

                sections.append(
                    DiffSection(
                        TranslatedFormsSection(old_proposal),
                        TranslatedFormsSection(new_proposal),
                    )
                )

                if has_legacy_docs:
                    old_extra_docs = get_extra_documents(old_proposal)
                    new_extra_docs = get_extra_documents(new_proposal)

                    if old_extra_docs or new_extra_docs:
                        for num, zipped_extra_docs in enumerate(
                            zip_equalize_lists(old_extra_docs, new_extra_docs)
                        ):
                            sections.append(DiffSection(*multi_sections()))

                sections.append(
                    DiffSection(
                        DMPFileSection(old_proposal), DMPFileSection(new_proposal)
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


