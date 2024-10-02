from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _
from main.utils import renderable
from .kinds import ATTACHMENT_CHOICES

from cdh.files.db import FileField as CDHFileField

# Create your models here.

class Attachment(models.Model, renderable):

    template_name = "attachments/attachment_model.html"
    author = models.ForeignKey(
        get_user_model(),
        related_name="created_attachments",
        null=True,
        on_delete=models.SET_NULL,
        default=None,
    )
    upload = CDHFileField(
        verbose_name=_("Bestand"),
        help_text=_("Selecteer hier het bestand om toe te voegen."),
    )
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

    def get_correct_submodel(self):
        from .kinds import get_kind_from_str
        kind = get_kind_from_str(self.kind)
        key = kind.attachment_class.__name__
        return getattr(self, key)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["attachment"] = self
        return context

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
