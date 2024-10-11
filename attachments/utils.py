from django.template.loader import get_template
from django.utils.translation import gettext as _
from django.urls import reverse

from main.utils import renderable
from proposals.models import Proposal
from studies.models import Study

from attachments.models import Attachment

class AttachmentKind:
    """Defines a kind of file attachment and when it is required."""

    db_name = ""
    name = ""
    description = ""
    max_num = None
    attached_field = "attachments"

    def __init__(self, owner=None):
        self.owner = owner

    @classmethod
    def from_proposal(cls, proposal, attachment):
        kind = get_kind_from_str(attachment.kind)
        if kind.model is Proposal:
            return kind(owner=proposal)
        # This might be more efficient in a QS
        for study in proposal.studies:
            if attachment in study.attachments:
                return kind(owner=study)
        msg = f"Attachment {attachment.pk} not found for proposal {proposal}"
        raise KeyError(msg)

    def get_slots(self, manager=None):
        slots = []
        for inst in self.get_instances_for_object():
            slots.append(AttachmentSlot(self, attachment=inst, manager=manager,))
        for i in range(self.still_required()):
            slots.append(AttachmentSlot(self, manager=manager,))
        return slots

    def num_required(self):
        return 0

    def num_suggested(self):
        return 0

    def num_provided(self):
        return self.get_instances_for_object().count()

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
            "other_pk": self.owner.pk,
            "kind": self.db_name,
        }
        return reverse("proposals:attach_file", kwargs=url_kwargs)


class AttachmentSlot(renderable):

    template_name = "attachments/slot.html"

    def __init__(
            self,
            attached_object,
            attachment=None,
            manager=None,
            kind=None,
    ):
        self.attachment = attachment
        self.attached_object = attached_object
        self.desiredness = _("Verplicht")
        self.manager = manager
        self.kind = kind
        self.match_attachment()

    def match_attachment(self):
        """
        Tries to fill this slot with an existing attachment.
        """
        for instance in self.get_instances_for_slot():
            self.attachment = instance
            break

    def desiredness(self):
        if self.force_required:
            return self.force_desiredness

    def get_instances_for_slot(self,):
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

    def get_attach_url(self,):
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

    def get_delete_url(self,):
        return reverse(
            "proposals:detach",
            kwargs={
                "attachment_pk": self.attachment.pk,
                "other_pk": self.attached_object.pk,
            }
        )

    def get_edit_url(self,):
        return reverse(
            "proposals:update_attachment",
            kwargs={
                "attachment_pk": self.attachment.pk,
                "other_pk": self.attached_object.pk,
            }
        )

def get_kind_from_str(db_name):
    from attachments.kinds import ATTACHMENTS
    kinds = {
        kind.db_name: kind
        for kind in ATTACHMENTS
    }
    return kinds[db_name]
