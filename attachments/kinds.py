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

#####################
# Information letters
#####################

class InformationLetterAnonymous(StudyAttachmentKind):

    db_name = "information_letter_anonymous"
    name = _("Informatiebrief anoniem onderzoek")
    description = _("Je verzamelt en verwerkt de gegevens van je deelnemers"
                    " anoniem. Je moet je deelnemers dan wél informeren op"
                    " ethische gronden (zodat ze kunnen beslissen of ze"
                    " vrijwillig willen meedoen), maar omdat de AVG niet"
                    " van toepassing is op anonieme gegevens, hoef je geen"
                    " informatie te verstrekken over de verwerking van"
                    " persoonsgegevens.")
    desiredness = desiredness.REQUIRED

class InformationLetterPublicInterest(StudyAttachmentKind):

    db_name = "information_letter_public_interest"
    name = _("Informatiebrief algemeen belang")
    description = _("Je kiest ervoor om de verwerking van persoonsgegevens te"
                    " baseren op het algemeen belang. In beginsel is dit"
                    " de standaardwerkwijze. \n"
                    "Let op! Voor bepaalde aspecten van je onderzoek kan het"
                    " desondanks nodig zijn om toestemming te vragen.")
    desiredness = desiredness.REQUIRED

class InformationLetterConsent(StudyAttachmentKind):

    db_name = "information_letter_consent"
    name = _("Informatiebrief toestemming")
    description = _("Er zijn redenen om de verwerking van persoonsgegevens"
                    " te baseren op toestemming van de deelnemers."
                    " Bijvoorbeeld als er gevoelige data wordt verzameld of"
                    " er met minderjarigen wordt gewerkt.")
    desiredness = desiredness.REQUIRED

LEGAL_BASIS_KIND_DICT = {
    Study.LegalBases.ANONYMOUS: InformationLetterAnonymous,
    Study.LegalBases.CONSENT: InformationLetterConsent,
    Study.LegalBases.PUBLIC_INTEREST: InformationLetterPublicInterest,    
}

###############
# Consent forms
###############

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
    InformationLetterAnonymous,
    InformationLetterPublicInterest,
    InformationLetterConsent,
    ConsentForm,
]

PROPOSAL_ATTACHMENTS = [
    DataManagementPlan,
    OtherProposalAttachment,
]

ATTACHMENTS = PROPOSAL_ATTACHMENTS + STUDY_ATTACHMENTS
