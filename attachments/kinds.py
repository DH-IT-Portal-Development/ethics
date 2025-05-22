from django.utils.translation import gettext_lazy as _
from django.urls import reverse

from proposals.models import Proposal
from studies.models import Study
from main.utils import renderable
from attachments.models import ProposalAttachment, StudyAttachment
from attachments.utils import AttachmentKind, desiredness

from django.utils.functional import lazy
from django.utils.safestring import mark_safe, SafeString

mark_safe_lazy = lazy(mark_safe, SafeString)


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
    description = _(
        "Je verzamelt en verwerkt de gegevens van je deelnemers"
        " anoniem. Je moet je deelnemers dan wél informeren op"
        " ethische gronden (zodat ze kunnen beslissen of ze"
        " vrijwillig willen meedoen), maar omdat de AVG niet"
        " van toepassing is op anonieme gegevens, hoef je geen"
        " informatie te verstrekken over de verwerking van"
        " persoonsgegevens."
    )
    desiredness = desiredness.REQUIRED
    more_info_link = _("https://intranet.uu.nl/media/34426")



class InformationLetterPublicInterest(StudyAttachmentKind):

    db_name = "information_letter_public_interest"
    name = _("Informatiebrief algemeen belang")
    description = _(
        "Je kiest ervoor om de verwerking van persoonsgegevens te"
        " baseren op het algemeen belang. In beginsel is dit"
        " de standaardwerkwijze. \n"
        "Let op! Voor bepaalde aspecten van je onderzoek kan het"
        " desondanks nodig zijn om toestemming te vragen."
    )
    desiredness = desiredness.REQUIRED
    more_info_link = _("https://intranet.uu.nl/media/34425")

class InformationLetterConsent(StudyAttachmentKind):

    db_name = "information_letter_consent"
    name = _("Informatiebrief toestemming")
    description = _(
        "Er zijn redenen om de verwerking van persoonsgegevens"
        " te baseren op toestemming van de deelnemers."
        " Bijvoorbeeld als er gevoelige data wordt verzameld of"
        " er met minderjarigen wordt gewerkt."
    )
    desiredness = desiredness.REQUIRED
    more_info_link = _("https://intranet.uu.nl/media/34428")

LEGAL_BASIS_KIND_DICT = {
    Study.LegalBases.ANONYMOUS: InformationLetterAnonymous,
    Study.LegalBases.CONSENT: InformationLetterConsent,
    Study.LegalBases.PUBLIC_INTEREST: InformationLetterPublicInterest,
}


###############
# Consent forms
###############


class ConsentFormAdults(StudyAttachmentKind):

    db_name = "consent_form_adults"
    name = _("Toestemmingsverklaring 16+")
    description = _(
        "Je baseert de verwerking van persoonsgegevens binnen je onderzoek op"
        " de wettelijke grondslag toestemming. De deelnemers zijn volwassenen"
        " (16 jaar en ouder)."
    )
    desiredness = desiredness.REQUIRED
    more_info_link = _("https://intranet.uu.nl/media/34434")
    more_info_link_name = _("Toestemmingsverklaring Toestemming")

class ConsentPublicInterestSpecialDetails(StudyAttachmentKind):

    db_name = "consent_public_interest_special_details"
    name = _("Toestemmingsverklaring algemeen belang bijzondere persoonsgegevens")
    description = _(
        "Je baseert de verwerking van persoonsgegevens binnen je onderzoek"
        " weliswaar op de wettelijke grondslag algemeen belang, maar je"
        " verzamelt zgn. bijzondere persoonsgegevens externe link en daarvoor"
        " heb je toestemming nodig."
    )
    desiredness = desiredness.REQUIRED
    more_info_link = _("https://intranet.uu.nl/media/34431")

class ConsentChildrenParents(StudyAttachmentKind):

    db_name = "consent_children_w_parents"
    name = _("Toestemmingsverklaring kinderen tot 16 jaar, ouders of voogden aanwezig")
    description = _(
        "Je baseert de verwerking van persoonsgegevens binnen je"
        " onderzoek op de wettelijke grondslag toestemming. De"
        " deelnemers zijn kinderen jonger dan 16 jaar en minimaal"
        " één van de ouders of voogden is bij het onderzoek aanwezig."
    )
    desiredness = desiredness.REQUIRED
    more_info_link = _("https://intranet.uu.nl/media/34432")

class ConsentChildrenNoParents(StudyAttachmentKind):

    db_name = "consent_children_no_parents"
    name = _("Toestemmingsverklaring kinderen tot 16 jaar, ouders of voogden afwezig")
    description = _(
        "Je baseert de verwerking van persoonsgegevens binnen je"
        " onderzoek op de wettelijke grondslag toestemming. De"
        " deelnemers zijn kinderen jonger dan 16 jaar en er zijn"
        " geen ouders of voogden aanwezig."
    )
    desiredness = desiredness.REQUIRED
    more_info_link = _("https://intranet.uu.nl/media/34433")

####################
# Recordings consent
####################


class AgreementRecordingsAdults(StudyAttachmentKind):

    db_name = "agreement_av_recordings_adults"
    name = _("Akkoordverklaring beeld- en geluidsopnames algemeen belang 16+")
    description = _(
        "Je baseert de verwerking van persoonsgegevens op de wettelijke grondslag "
        "algemeen belang, maar je maakt beeld- en/of geluidsopnames van volwassenen "
        "en daar moeten je deelnemers op ethische gronden mee instemmen. Ook voor het "
        "verdere gebruik van die opnames kun je de afspraken schriftelijk vastleggen."
    )
    desiredness = desiredness.REQUIRED
    more_info_link = _("https://intranet.uu.nl/system/files/gw_Akkoordverklaring%20-%20grondslag%20Algemeen%20belang%20-%20beeld-%20en%20geluidsopnames.docx")
    more_info_link_name = _("Akkoordverklaring - grondslag Algemeen belang - beeld- en geluidsopnames")

class AgreementRecordingsChildrenParents(StudyAttachmentKind):

    db_name = "agreement_av_recordings_children_w_parents"
    name = _(
        "Akkoordverklaring beeld- en geluidsopnames tot 16 jaar, ouders of voogden aanwezig"
    )
    description = _(
        "Je baseert de verwerking van persoonsgegevens op de"
        " wettelijke grondslag algemeen belang, maar je maakt beeld- en/of"
        " geluidsopnames van kinderen in aanwezigheid van diens ouders of voogden."
        " Daar moeten de ouders of voogden van de deelnemers op ethische gronden"
        " mee instemmen. Ook voor het verdere gebruik van die opnames kun"
        " je de afspraken schriftelijk vastleggen."
    )
    desiredness = desiredness.REQUIRED
    more_info_link = _("https://intranet.uu.nl/system/files/gw_Akkoordverklaring%20-%20Algemeen%20belang%20-%20Opnames%20kind%20-%20ouders-voogden%20WEL%20aanwezig.docx")
    more_info_link_name = _("Akkoordverklaring – Algemeen belang - Opnames kind - ouders-voogden aanwezig bij onderzoek")

class AgreementRecordingsChildrenNoParents(StudyAttachmentKind):

    db_name = "agreement_av_recordings_children_no_parents"
    name = _(
        "Akkoordverklaring beeld- en geluidsopnames tot 16 jaar, ouders of voogden afwezig"
    )
    description = _(
        "Je baseert de verwerking van persoonsgegevens op de"
        " wettelijke grondslag algemeen belang, maar je maakt beeld- en/of"
        " geluidsopnames van kinderen in afwezigheid van diens ouders of voogden."
        " Daar moeten de ouders of voogden van de deelnemers op ethische gronden"
        " mee instemmen. Ook voor het verdere gebruik van die opnames kun"
        " je de afspraken schriftelijk vastleggen."
    )
    desiredness = desiredness.REQUIRED
    more_info_link = _("https://intranet.uu.nl/system/files/gw_Akkoordverklaring%20-%20Algemeen%20belang%20-%20Opnames%20kind%20-%20ouders-voogden%20NIET%20aanwezig.docx")
    more_info_link_name = _("Akkoordverklaring - Algemeen belang - Opnames kind - ouders-voogden NIET aanwezig")

class ScriptVerbalConsentRecordings(StudyAttachmentKind):

    db_name = "script_verbal_consent_recordings"
    name = _("Script voor mondelinge toestemming opnames")
    description = _(
        "Je interviewt deelnemers en je maakt daarvan beeld- en/of"
        " geluidsopnames. De toestemming daarvoor, en de eventuele"
        " toestemming en afspraken met betrekking tot andere aspecten van"
        " de verwerking van persoonsgegevens, leg je vast in een aparte opname."
    )
    desiredness = desiredness.REQUIRED
    more_info_link = _("https://intranet.uu.nl/media/34429")

##############
# School stuff
##############


class SchoolInformationLetter(ProposalAttachmentKind):

    db_name = "school_information_letter"
    name = _("Informatiebrief gatekeeper/schoolleiding")
    description = _(
        "Je wilt onderzoek gaan doen binnen een bepaalde instelling (bijv."
        " een school) en je verzoekt de leiding van die instelling om"
        " medewerking. Voor het maken van een geïnformeerde keuze moet de"
        " leiding van de instelling op de hoogte zijn van de opzet van je"
        " onderzoek en van allerlei praktische aspecten."
    )
    desiredness = desiredness.REQUIRED
    more_info_link = _("https://intranet.uu.nl/media/34427")

class SchoolConsentForm(ProposalAttachmentKind):

    db_name = "school_consent_form"
    name = _("Akkoordverklaring gatekeeper/schoolleiding")
    description = _(
        "Je wilt onderzoek gaan doen binnen een bepaalde instelling (bijv."
        " een school) en je verzoekt de leiding van die instelling om"
        " medewerking. De schoolleiding moet, na goed geïnformeerd te zijn"
        " toestemming geven voor het onderzoek."
    )
    desiredness = desiredness.REQUIRED
    more_info_link = _("https://intranet.uu.nl/media/34424")

#############
# Other stuff
#############


class DataManagementPlan(ProposalAttachmentKind):

    db_name = "dmp"
    name = _("Data Management Plan")
    #requires acces to intranet something every user should have
    description = _(
        "Een Data Management Plan (DMP) is een document, dat voorafgaand aan een "
        "onderzoeksproject wordt opgesteld. Hierin worden alle aspecten omtrent de "
        "omgang met onderzoeksdata, tijdens en na afloop van het onderzoek, "
        "uiteengezet."
        )

    desiredness = desiredness.RECOMMENDED
    more_info_link = _("https://intranet.uu.nl/system/files/2025%20-%20Dataset-list.docx")

    def num_recommended(self):
        return 1


class OtherAttachment(ProposalAttachmentKind):

    db_name = "other"
    name = _("Overig bestand")
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
    AgreementRecordingsAdults,
    AgreementRecordingsChildrenParents,
    AgreementRecordingsChildrenNoParents,
    ScriptVerbalConsentRecordings,
    ConsentPublicInterestSpecialDetails,
    ConsentChildrenParents,
    ConsentChildrenNoParents,
    ConsentFormAdults,
]

PROPOSAL_ATTACHMENTS = [
    SchoolInformationLetter,
    SchoolConsentForm,
    DataManagementPlan,
    OtherAttachment,
]

ATTACHMENTS = PROPOSAL_ATTACHMENTS + STUDY_ATTACHMENTS

KIND_CHOICES = list(((kind.db_name, kind.name) for kind in ATTACHMENTS))
