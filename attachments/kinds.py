from django.utils.translation import gettext as _
from django.urls import reverse

from proposals.models import Proposal

class AttachmentKind:
    """Defines a kind of file attachment and when it is required."""

    db_name = ""
    name = ""
    description = ""
    max_num = None
    attached_model = Proposal
    attached_field = "attachments"

    def __init__(self, obj):
        self.object = obj

    def get_instances_for_proposal(self):
        manager = getattr(self.object, self.attached_field)
        return manager.filter(kind=self.db_name)

    def num_required(self):
        return 1

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
    name = _("Overige bestanden")
    description = _("Voor alle overige soorten bestanden")

    def num_required(self):
        return 0


ATTACHMENTS = [
    InformationLetter,
    ConsentForm,
    DataManagementPlan,
    OtherAttachment,
]
ATTACHMENT_CHOICES = [
    (a.db_name, a.name) for a in ATTACHMENTS
]
