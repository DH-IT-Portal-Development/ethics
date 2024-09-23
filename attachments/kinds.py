from django.utils.translation import gettext as _
from django.urls import reverse

from proposals.models import Proposal
from studies.models import Study
from main.utils import renderable

class AttachmentKind:
    """Defines a kind of file attachment and when it is required."""

    db_name = ""
    name = ""
    description = ""
    max_num = None
    attached_field = "attachments"

    def __init__(self, obj):
        self.object = obj

    def get_slots(self):
        slots = []
        for inst in self.get_instances_for_object():
            slots.append(AttachmentSlot(self, inst,))
        for i in range(self.still_required()):
            slots.append(AttachmentSlot(self, inst,))
        return slots

    def get_instances_for_object(self):
        manager = getattr(self.object, self.attached_field)
        return manager.filter(kind=self.db_name)

    def num_required(self):
        return 0

    def num_suggested(self):
        return 0

    def num_provided(self):
        return self.get_instances_for_proposal().count()

    def still_required(self):
        return self.num_required() - self.num_provided()

    def test_required(self):
        """Returns False if the given proposal requires this kind
        of attachment"""
        return self.num_required() > self.num_provided()

    def test_recommended(self):
        """Returns True if the given proposal recommends, but does not
        necessarily require this kind of attachment"""
        return True

    def get_attach_url(self):
        url_kwargs = {
            "other_pk": self.object.pk,
            "kind": self.db_name,
        }
        return reverse("proposals:attach_file", kwargs=url_kwargs)

class ProposalAttachmentKind(AttachmentKind):

    attached_object = Proposal

class StudyAttachmentKind(AttachmentKind):

    attached_object = Study

class InformationLetter(StudyAttachmentKind):

    db_name = "information_letter"
    name = _("Informatiebrief")
    description = _("Omschrijving informatiebrief")

    def num_required(self,):
        return 1

class ConsentForm(AttachmentKind):

    db_name = "consent_form"
    name = _("Toestemmingsverklaring")
    description = _("Omschrijving toestemmingsverklaring")

class DataManagementPlan(ProposalAttachmentKind):

    db_name = "dmp"
    name = _("Data Management Plan")
    description = _("Omschrijving DMP")

    def num_recommended(self):
        return 1

class OtherProposalAttachment(ProposalAttachmentKind):

    db_name = "other"
    name = _("Overige bestanden")
    description = _("Voor alle overige soorten bestanden")

    def num_required(self):
        return 0

    def num_suggested(self):
        """
        You may always add another miscellaneous file."""
        return self.num_provided + 1


STUDY_ATTACHMENTS = [
    InformationLetter,
    ConsentForm,
]


PROPOSAL_ATTACHMENTS = [
    DataManagementPlan,
    OtherProposalAttachment,
]

ATTACHMENTS = PROPOSAL_ATTACHMENTS + STUDY_ATTACHMENTS

ATTACHMENT_CHOICES = [
    (a.db_name, a.name) for a in ATTACHMENTS
]

class AttachmentSlot(renderable):

    template_name = "attachments/slot.html"

    def __init__(self, kind, attachment=None):
        self.kind = kind
        self.attachment = attachment

    def get_attach_url(self,):
        return "#"

    def get_delete_url(self,):
        return "#"

class ProposalAttachments:
    """
    A utility class that provides most functions related to a proposal's
    attachments. The algorithm with which required attachments are determined
    is as follows:

    1. Collect all existing attachments for proposal and studies
    2. Match all existing attachments to kinds
    3. Complement existing attachments with additional kind instances to
       represent yet to be fulfilled requirements

    This happens for the proposal as a whole and each of its studies.
    """

    def __init__(self, proposal):
        self.proposal = proposal
        self.proposal_kinds = self.walk_proposal()
        self.study_kinds = self.walk_all_studies()
        self.match_slots()

    def match_slots(self,):
        self.proposal_slots = []
        for kind in self.proposal_kinds:
            self.proposal_slots += kind.get_slots()
        self.study_slots = {}
        for study, kinds in self.study_kinds:
            self.study_slots[study] = []
            for kind in kinds:
                self.study_slots[study] += kind.get_slots()

    def walk_proposal(self):
        kinds = []
        for kind in PROPOSAL_ATTACHMENTS:
            kinds.append(
                kind(self.proposal),
            )
        return kinds

    def walk_all_studies(self):
        study_dict = {}
        for study in self.proposal.study_set.all():
            study_dict[study] = self.walk_study(study)
        return study_dict

    def walk_study(self, study):
        kinds = []
        for kind in STUDY_ATTACHMENTS:
            kinds.append(
                kind(study),
            )
        return kinds
