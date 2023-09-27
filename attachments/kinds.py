from django.utils.translation import gettext as _

class AttachmentKind:
    """Defines a kind of file attachment and when it is required."""

    db_name = ""
    name = ""
    description = ""
    max_num = None

    def test_required(self, proposal):
        """Returns False if the given proposal requires this kind
        of attachment"""
        return False

    def test_recommended(self, proposal):
        """Returns True if the given proposal recommends, but does not
        necessarily require this kind of attachment"""
        return True


class InformationLetter(AttachmentKind):

    db_name = "information_letter"
    name = _("Informatiebrief")
    description = _("Omschrijving informatiebrief")

class ConsentForm(AttachmentKind):

    db_name = "consent_form"
    name = _("Toestemmingsverklaring")
    description = _("Omschrijving toestemmingsverklaring")

class DataManagementPlan(AttachmentKind):

    db_name = "dmp"
    name = _("Data Management Plan")
    description = _("Omschrijving DMP")

class OtherAttachment(AttachmentKind):

    db_name = "other"
    name = _("Overig bestand")
    description = _("Voor alle overige soorten bestanden")


ATTACHMENTS = [
    InformationLetter,
    ConsentForm,
    DataManagementPlan,
]
ATTACHMENT_CHOICES = [
    (a.db_name, a.name) for a in ATTACHMENTS
]
