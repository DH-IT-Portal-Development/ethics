import mimetypes

from django.template.loader import get_template
from django.utils.translation import gettext as _
from django.urls import reverse

from main.utils import renderable
from proposals.models import Proposal
from studies.models import Study


class desiredness:
    REQUIRED = _("Verplicht")
    RECOMMENDED = _("Aangeraden")
    OPTIONAL = _("Optioneel")
    EXTRA = _("Extra")


class AttachmentKind:
    """Defines a kind of file attachment and when it is required."""

    db_name = ""
    name = ""
    description = ""
    max_num = None
    attached_field = "attachments"
    desiredness = desiredness.OPTIONAL


class AttachmentSlot(renderable):

    template_name = "attachments/slot.html"

    def __init__(
        self,
        attached_object,
        attachment=None,
        kind=None,
        force_desiredness=None,
    ):
        self.attachment = attachment
        self.attached_object = attached_object
        self.kind = kind
        self.force_desiredness = force_desiredness

    def match(self, exclude):
        """
        Tries to fill this slot with an existing attachment that is not
        in the exclusion set of already matched attachments.
        """
        for instance in self.get_instances_for_slot():
            if instance not in exclude:
                self.attachment = instance
                break

    @property
    def desiredness(self):
        if self.force_desiredness:
            return self.force_desiredness
        return self.kind.desiredness

    def get_instances_for_slot(
        self,
    ):
        """
        Returns a QS of existing Attachments that potentially
        could fit in this slot.
        """
        manager = getattr(
            self.attached_object,
            "attachments",
        )
        if self.kind:
            manager = manager.filter(kind=self.kind.db_name)
        return manager.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["slot"] = self
        context["proposal"] = self.get_proposal()
        return context

    def get_proposal(self):
        if type(self.attached_object) is Proposal:
            return self.attached_object
        else:
            return self.attached_object.proposal

    def get_attach_url(
        self,
    ):
        url_name = {
            Proposal: "proposals:attach_proposal",
            Study: "proposals:attach_study",
        }[type(self.attached_object)]
        reverse_kwargs = {
            "other_pk": self.attached_object.pk,
        }
        if self.kind:
            reverse_kwargs["kind"] = self.kind.db_name
        return reverse(
            url_name,
            kwargs=reverse_kwargs,
        )

    def get_delete_url(
        self,
    ):
        return reverse(
            "proposals:detach",
            kwargs={
                "attachment_pk": self.attachment.pk,
                "other_pk": self.attached_object.pk,
            },
        )

    def get_edit_url(
        self,
    ):
        return reverse(
            "proposals:update_attachment",
            kwargs={
                "attachment_pk": self.attachment.pk,
                "other_pk": self.attached_object.pk,
            },
        )

def attachment_filename_generator(file):
    #get the correct attachment
    try:
        attachment = ProposalAttachment.objects.get(upload=file.file_instance)
        proposal = attachment.attached_to.last()
        trajectory = None
    except ProposalAttachment.DoesNotExist:
        attachment = StudyAttachment.objects.get(upload=file.file_instance)
        study = attachment.attached_to.last()
        proposal = study.proposal
        trajectory = f"T{study.order}"
        
    chamber = proposal.reviewing_committee.name
    lastname = proposal.created_by.last_name
    refnum = proposal.reference_number
    kind = attachment.kind
    extension = mimetypes.guess_extension(file.file_instance.content_type)

    fn_parts = [
            "FETC",
            chamber,
            refnum,
            lastname,
            trajectory,
            kind,
        ]

    # Translations will trip up join(), so we convert them here
    fn_parts = [str(p) for p in fn_parts if p]

    return "-".join(fn_parts) + extension


def get_kind_from_str(db_name):
    from attachments.kinds import ATTACHMENTS

    kinds = {kind.db_name: kind for kind in ATTACHMENTS}
    return kinds[db_name]
