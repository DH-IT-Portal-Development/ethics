from django.utils.translation import gettext as _
from django.urls import reverse

from proposals.models import Proposal
from studies.models import Study
from main.utils import renderable
from attachments.models import ProposalAttachment, StudyAttachment
from attachments.utils import AttachmentKind, desiredness


class ProposalAttachmentKind(AttachmentKind):

    attached_object = Proposal
    attachment_class = ProposalAttachment

class StudyAttachmentKind(AttachmentKind):

    attached_object = Study
    attachment_class = StudyAttachment

class InformationLetter(StudyAttachmentKind):

    db_name = "information_letter"
    name = _("Informatiebrief")
    description = _("Omschrijving informatiebrief")
    desiredness = desiredness.REQUIRED

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

