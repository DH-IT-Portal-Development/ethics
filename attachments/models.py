from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _
from main.utils import renderable
from .kinds import ATTACHMENT_CHOICES

from cdh.files.db import FileField as CDHFileField

# Create your models here.

class Attachment(models.Model, renderable):

    template_name = "attachment/attachment_model.html"
    upload = CDHFileField()
    parent = models.ForeignKey(
        "attachments.attachment",
        related_name="children",
        null=True,
        on_delete=models.SET_NULL,
        default=None,
    )
    kind = models.CharField(
        max_length=100,
        choices=ATTACHMENT_CHOICES,
        default=("", _("Gelieve selecteren")),
    )
    name = models.CharField(
        max_length=50,
        default="",
        help_text=_(
            "Geef je bestand een omschrijvende naam, het liefst "
            "maar enkele woorden."
        )
    )
    comments = models.TextField(
        max_length=2000,
        default="",
        help_text=_(
            "Geef hier je motivatie om dit bestand toe te voegen en waar "
            "je het voor gaat gebruiken tijdens je onderzoek. Eventuele "
            "opmerkingen voor de FETC kun je hier ook kwijt."
        )
    )

class ProposalAttachment(Attachment,):
    attached_to = models.ManyToManyField(
        "proposals.Proposal",
        related_name="attachments",
    )

class StudyAttachment(Attachment,):
    attached_to = models.ManyToManyField(
        "studies.Study",
        related_name="attachments",
    )
