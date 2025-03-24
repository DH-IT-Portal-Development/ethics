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
    get_all_related,
    get_all_related_set,
    get_all_sessions,
    get_extra_documents,
    multi_sections,
    KindRow,
    AttachmentRow,
    UploadDateRow,
    ProvisionRow,
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

        if not obj.is_pre_assessment:
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

    section_title = _("Persoonsgegevens")
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
    

class RegistrationSection(BaseSection):
    """This class receives a proposal.study object
    Note the overwritten __init__ method for adding a sub_title."""

    section_title = _("Registratie")
    row_fields = [
        "registrations",
        "registrations_details",
        "registration_kinds",
        "registration_kinds_details",
    ]

    def __init__(self, obj):
        super().__init__(obj)
        self.sub_title = self.get_sub_title(self.obj, "study")

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
    """
    This section, uniquely, works with a AttachmentSlot as its obj. This is the
    only section that does not receive a Django model as its obj, which leads
    to the funky self.make_row_field. KindRow is only used here.
    """

    section_title = ""

    row_fields = [
        "upload",
        "upload_date",
        "provision",
        "name",
        "comments",
        "kind",
    ]

    def __init__(self, obj, sub_title, proposal):
        super().__init__(obj)
        self.sub_title = sub_title
        self.proposal = proposal

    def make_row_for_field(self, field):

        # "kind" and "upload" require slots as their obj, other fields receive
        # the attachment as their obj.
        if field == "kind":
            return KindRow(self.obj, self.obj.attachment, field)
        if field == "upload":
            return AttachmentRow(self.obj, field, self.proposal)
        else:
            obj = self.obj.attachment

        if field == "upload_date":
            return UploadDateRow(obj, field)
        if field == "provision":
            return ProvisionRow(self.obj, field)

        return Row(obj, field, self.proposal)


###############
# FinalSections
###############


class DMPSection(PageBreakMixin, BaseSection):
    """
    This class receives a proposal object
    """

    section_title = _("Data Management")

    row_fields = ["privacy_officer"]


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


#####################
# Create the full PDF
#####################


def create_context_pdf(context, proposal):
    """A function to create the context for the PDF, which gets called in the ProposalAsPdf view."""

    sections = []

    sections.append(GeneralSection(proposal))

    if not proposal.is_pre_approved:
        if hasattr(proposal, "wmo"):
            sections.append(WMOSection(proposal.wmo))

            if proposal.wmo.status != proposal.wmo.WMOStatuses.NO_WMO:
                sections.append(METCSection(proposal.wmo))

            if not proposal.is_pre_assessment:

                sections.append(TrajectoriesSection(proposal))

                if proposal.wmo.status == proposal.wmo.WMOStatuses.NO_WMO:
                    for study in proposal.study_set.all():
                        sections.append(StudySection(study))
                        sections.append(PersonalDataSection(study))
                        sections.append(RegistrationSection(study))
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

                    sections.append(KnowledgeSecuritySection(proposal))

                    sections.append(DMPSection(proposal))

                    sections.extend(
                        AllAttachmentSectionsPDF(proposal).get_all_attachment_sections()
                    )

                    sections.append(TranslatedFormsSection(proposal))

                sections.append(EmbargoSection(proposal))

            elif proposal.is_pre_assessment:
                sections.extend(
                    AllAttachmentSectionsPDF(proposal).get_all_attachment_sections()
                )
    elif proposal.is_pre_approved:
        sections.append(DMPSection(proposal))

        sections.extend(
            AllAttachmentSectionsPDF(proposal).get_all_attachment_sections()
        )

        sections.append(TranslatedFormsSection(proposal))

        sections.append(EmbargoSection(proposal))
    sections.append(CommentsSection(proposal))

    context["sections"] = sections

    return context


class AllAttachmentSectionsPDF:
    """
    Class to create sections for attachments in the PDF.
    Many of these class methods receive a proposal explicitly and not from self,
    so that they can be re-used for creating sections for the diff
    """

    def __init__(self, proposal):
        self.proposal = proposal

    def get_all_attachment_sections(self):
        """
        Returns a list of Attachment sections, along with TitleSections to organize
        the sections. Only used for PDF.
        """
        attachment_sections = []

        slot_dict = self._all_attachments_dict(self.proposal)

        for owner in slot_dict:
            if slot_dict[owner]:
                title = self._create_object_heading(owner, self.proposal)
                for index, slot in enumerate(slot_dict[owner]):
                    att_section = self._create_attachment_section(slot)
                    # Add a section title to the first attachment for an owner
                    if index == 0:
                        att_section.section_title = title
                    attachment_sections.append(att_section)

        return attachment_sections

    def _all_slots_list(self, proposal):
        """
        Returns a list of all slots for a specific proposal
        """
        from proposals.utils.stepper import Stepper

        stepper = Stepper(proposal)
        slots = stepper.filled_slots

        return slots

    def _all_owners_list(self, proposal):
        """
        Returns a list of all possible owners of attachments for a given proposal
        """
        return [proposal] + list(proposal.study_set.all())

    def _all_attachments_dict(self, proposal):
        """
        Returns a dictionary where the objects are the keys and the attachments
        are stored in a list as the value
        """

        slots = self._all_slots_list(proposal)

        objects = self._all_owners_list(proposal)
        slot_dict = {obj: [] for obj in objects}
        for slot in slots:
            relevant_owner = slot.attachment.get_owner_for_proposal(proposal)
            slot_dict[relevant_owner].append(slot)

        return slot_dict

    def _create_object_heading(self, owner, proposal):
        """
        Generate a title for a study or proposal to which attachments are attached
        """
        if owner == proposal:
            title = _("Documenten - Aanvraag in het geheel")
        elif proposal.study_set.count() == 1:
            title = _("Documenten - Het hoofdtraject")
        else:
            title = _("Documenten - Traject ") + str(owner.order) + ": " + owner.name
        return title

    def _create_attachment_section(self, slot):
        """
        Creates an AttachmentSection, where a specific attachment can
        optionally be supplied eg. attachment.parent (used for the diff)
        """
        return AttachmentSection(
            slot,
            sub_title=slot.kind.name,
            proposal=slot.get_proposal(),
        )


######################
# Create the full diff
######################


def create_context_diff(context, old_proposal, new_proposal):
    """A function to create the context for the diff page."""

    sections = []

    sections.append(
        DiffSection(GeneralSection(old_proposal), GeneralSection(new_proposal))
    )

    if not new_proposal.is_pre_approved:

        if hasattr(new_proposal, "wmo"):
            sections.append(
                DiffSection(WMOSection(old_proposal.wmo), WMOSection(new_proposal.wmo))
            )

            if (
                new_proposal.wmo.status != new_proposal.wmo.WMOStatuses.NO_WMO
                or old_proposal.wmo.status != old_proposal.wmo.WMOStatuses.NO_WMO
            ):
                sections.append(
                    DiffSection(
                        METCSection(old_proposal.wmo), METCSection(new_proposal.wmo)
                    )
                )

            if not new_proposal.is_pre_assessment:
                sections.append(
                    DiffSection(
                        TrajectoriesSection(old_proposal),
                        TrajectoriesSection(new_proposal),
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
                            DiffSection(
                                *multi_sections(PersonalDataSection, both_studies)
                            )
                        )

                        sections.append(
                            DiffSection(
                                *multi_sections(RegistrationSection, both_studies)
                            )
                        )

                        if (
                            old_study is not None
                            and old_study.get_intervention()
                            or new_study is not None
                            and new_study.get_intervention()
                        ):
                            interventions = get_all_related(
                                both_studies, "intervention"
                            )

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
                            old_sessions_set, new_sessions_set = get_all_sessions(
                                both_studies,
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
                                        *multi_sections(
                                            TasksOverviewSection, both_sessions
                                        )
                                    )
                                )

                        sections.append(
                            DiffSection(
                                *multi_sections(StudyOverviewSection, both_studies)
                            )
                        )

                    sections.append(
                        DiffSection(
                            KnowledgeSecuritySection(old_proposal),
                            KnowledgeSecuritySection(new_proposal),
                        )
                    )

                    sections.append(
                        DiffSection(DMPSection(old_proposal), DMPSection(new_proposal))
                    )

                    sections.extend(
                        AllAttachmentSectionsDiff(
                            old_proposal, new_proposal
                        ).get_all_attachment_sections_diff()
                    )

                    sections.append(
                        DiffSection(
                            TranslatedFormsSection(old_proposal),
                            TranslatedFormsSection(new_proposal),
                        )
                    )

                sections.append(
                    DiffSection(
                        EmbargoSection(old_proposal), EmbargoSection(new_proposal)
                    )
                )
            elif new_proposal:
                sections.extend(
                    AllAttachmentSectionsDiff(
                        old_proposal, new_proposal
                    ).get_all_attachment_sections_diff()
                )
    elif new_proposal.is_pre_approved:
        sections.append(DiffSection(DMPSection(old_proposal), DMPSection(new_proposal)))

        sections.extend(
            AllAttachmentSectionsDiff(
                old_proposal, new_proposal
            ).get_all_attachment_sections_diff()
        )

        sections.append(
            DiffSection(
                TranslatedFormsSection(old_proposal),
                TranslatedFormsSection(new_proposal),
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


class AllAttachmentSectionsDiff(AllAttachmentSectionsPDF):
    """
    Class to create secitons for attachments in the Diff.
    Is quite a bit more complex, but uses a lot of class methods from the
    PDF generation.

    We mostly adhere to the structure of the new proposal for outlining this,
    but sometimes have to do some guesswork to make attachments that are unique
    to the old proposal fit somewhere sensibly.
    """

    def __init__(self, old_p, new_p):
        self.old_p = old_p
        self.new_p = new_p
        # get all slots for both proposals
        self.new_slots = self._all_slots_list(self.new_p)
        self.old_slots = self._all_slots_list(self.old_p)

    def get_all_attachment_sections_diff(self):
        attachment_sections = []

        att_dict = self._get_matches_from_slots(self.old_slots, self.new_slots)

        for owner_num in att_dict.keys():
            proposal = self.new_p
            if owner_num == 0:
                owner_obj = proposal
            else:
                try:
                    owner_obj = proposal.study_set.get(order=owner_num)
                except:
                    proposal = self.old_p
                    owner_obj = proposal.study_set.get(order=owner_num)
            title = self._create_object_heading(owner_obj, proposal)
            for index, att_list in enumerate(att_dict[owner_num]):
                # Add a section_title attribute to the first attachment of each owner
                if index == 0:
                    for att in att_list:
                        if att is not None:
                            att.section_title = title
                attachment_sections.append(DiffSection(*att_list))

        return attachment_sections

    def _get_order(self, slot):
        from proposals.models import Proposal

        if type(slot.attached_object) is Proposal:
            return 0
        return slot.attached_object.order

    def _insert_into_matches(self, old_slot, new_slot, matches):
        """
        Appends a tuple of AttachmentSections to the matches dict
        The keys are study.order or 0 for Proposals
        """
        if new_slot:
            order = self._get_order(new_slot)
        else:
            order = self._get_order(old_slot)
        if order not in matches.keys():
            matches[order] = []
        matches[order].append(
            (
                self._create_attachment_section(old_slot) if old_slot else None,
                self._create_attachment_section(new_slot) if new_slot else None,
            ),
        )
        return matches

    def _match_slot(self, slot, slots):
        """
        Attempts to match an new slot to an old slot by recursively looping
        over the old_slots. It returns a match if the attachment is unchanged
        or if the slot's attachment is a child of an attachment in the old_slots
        """
        if slots == []:
            # If we've run out of slots, no match was found
            return False
        potential_match = slots[0]
        # We match against the exact same attachment or its parent,
        # if it has one
        targets = [slot.attachment]
        if slot.attachment.parent:
            targets.append(slot.attachment.parent.get_correct_submodel())
        if potential_match.attachment in targets:
            # Success, return the match
            return potential_match
        # Else, continue with the next potential match
        return self._match_slot(slot, slots[1:])

    def _get_matches_from_slots(self, old_slots, new_slots, matches=False):
        """
        Tail recursive function that returns a dictionary of integers to tuples
        of (old, new) attachment slot sets, either of which may be None, but not
        both.
        """
        if not matches:
            matches = dict()
        if new_slots == []:
            # If we've run out of new slots, start going through the yet
            # unmatched old slots.
            if old_slots == []:
                # If no old slots remain, return the matches
                return matches
            unmatched_old_slot = old_slots[0]
            # We've already run out of new slots, so these must be
            # unmatched slots and we can just insert them.
            self._insert_into_matches(
                unmatched_old_slot,
                None,
                matches,
            )
            # Continue until old slots run out
            return self._get_matches_from_slots(
                old_slots[1:],
                new_slots,
                matches=matches,
            )
        current_slot = new_slots[0]
        match = self._match_slot(current_slot, old_slots)
        if match:
            # If we have a match, insert it and remove the matched
            # old slot from the pool
            self._insert_into_matches(match, current_slot, matches)
            old_slots.remove(match)
        else:
            self._insert_into_matches(None, current_slot, matches)
        # Continue with the next new slot
        return self._get_matches_from_slots(
            old_slots,
            new_slots[1:],
            matches=matches,
        )
