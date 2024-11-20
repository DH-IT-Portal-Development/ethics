from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _
from django.urls import reverse
from main.utils import renderable

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
        # It would be nice to be able to define fixed choices here.
        # But I haven't found a way to nicely import them from kinds.py
        # without circular imports. So for now we just set the choices in
        # whatever form needs them.
        # From Django 5 onwards we can define a callable to get
        # the choices which would be the preferred solution.
        default=("", _("Gelieve selecteren")),
    )
    name = models.CharField(
        max_length=50,
        default="",
        help_text=_(
            "Geef je bestand een omschrijvende naam, het liefst " "maar enkele woorden."
        ),
    )
    comments = models.TextField(
        max_length=2000,
        default="",
        help_text=_(
            "Geef hier optioneel je motivatie om dit bestand toe te voegen en "
            "waar "
            "je het voor gaat gebruiken tijdens je onderzoek. Eventuele "
            "opmerkingen voor de FETC kun je hier ook kwijt."
        ),
    )

    def get_owner_for_proposal(self, proposal):
        """
        Convenience function that delegates to submodels.
        """
        submodel = self.get_correct_submodel()
        return submodel.get_owner_for_proposal()

    def get_correct_submodel(self):
        if self.__class__.__name__ != "Attachment":
            # In this case, we're already dealing with a submodel
            return self
        submodels = [StudyAttachment, ProposalAttachment]
        # By default, lowering the class name is how subclassed model
        # relation names are generated by Django. That's why the following
        # lines work.
        # However, if we use a different related_name or run into a name
        # collision we'd have to be smarter about getting the submodel.
        for submodel in submodels:
            key = submodel.__name__.lower()
            if hasattr(self, key):
                return getattr(self, key)
        raise KeyError("Couldn't find a matching submodel.")

    def detach(self, other_object):
        """
        Remove an attachment from an owner object. If no other
        owner objects remain, delete the attachment.

        This method is simple enough to define for all submodels,
        assuming they use the attached_to attribute name. However,
        base Attachments do not have an attached_to attribute, so
        we have to defer to the submodel if detach is called on a
        base Attachment instance.
        """
        if self.__class__.__name__ == "Attachment":
            attachment = self.get_correct_submodel()
            return attachment.detach(other_object)
        # The following part only runs if called from a submodel
        if self.attached_to.count() > 1:
            self.attached_to.remove(other_object)
        else:
            self.delete()

    def get_download_url(self, proposal):
        return reverse(
            "proposals:download_attachment_original",
            kwargs={
                "proposal_pk": proposal.pk,
                "attachment_pk": self.pk,
            },
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["attachment"] = self
        return context


class ProposalAttachment(
    Attachment,
):
    attached_to = models.ManyToManyField(
        "proposals.Proposal",
        related_name="attachments",
    )

    def get_owner_for_proposal(
        self,
        proposal,
    ):
        """
        This method doesn't do much, it's just here to provide
        a consistent interface for getting owner objects.
        """
        return proposal


class StudyAttachment(
    Attachment,
):
    attached_to = models.ManyToManyField(
        "studies.Study",
        related_name="attachments",
    )

    def get_owner_for_proposal(
        self,
        proposal,
    ):
        """
        Gets the owner study based on given proposal.
        """
        return self.attached_to.get(proposal=proposal)
