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
        optionality_group=None,
    ):
        self.attachment = attachment
        self.attached_object = attached_object
        self.kind = kind
        self.force_desiredness = force_desiredness
        self.optionality_group = optionality_group
        if self.optionality_group:
            self.optionality_group.members.add(self)

    def match(self, exclude=[]):
        """
        Tries to find a matching attachment for this slot. If it finds one,
        it returns the attachment, otherwise it returns False.
        """
        for instance in self.get_instances_for_slot():
            if instance not in exclude:
                return instance
        return False

    def match_and_set(self, exclude):
        """
        Uses self.match() to find a matching attachment. If it finds one, it
        sets self.attachment and self.kind
        """
        matched_attachment = self.match(exclude=exclude)
        if matched_attachment:
            self.attachment = matched_attachment
            self.kind = get_kind_from_str(matched_attachment.kind)
            return self.attachment
        return False

    @property
    def classes(self):
        if self.required:
            if self.attachment:
                return "border-success"
            else:
                return "border-warning"
        return ""

    @property
    def desiredness(self):
        if self.force_desiredness:
            return self.force_desiredness
        return self.kind.desiredness

    @property
    def required(self):
        return self.desiredness is desiredness.REQUIRED

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
        context["classes"] = self.classes
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


class OptionalityGroup(renderable):

    template_name = "attachments/optionality_group.html"

    def __init__(self, members=set()):
        self.members = set(members)

    @property
    def count(
        self,
    ):
        return len(self.members)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["group"] = self
        return context


def merge_groups(slots):
    """
    Takes a list of slots and merges slots that belong to the same
    optionality group together. This results in a mixed output list
    of bare slots and optionality groups.
    """
    grouped = []
    for slot in slots:
        if not slot.optionality_group:
            # No group, so we just append it
            grouped.append(slot)
            continue
        if slot.optionality_group not in grouped:
            # We only append the group if it's not already in the
            # output list to avoid duplication
            grouped.append(slot.optionality_group)
    # Final pass to remove single-member groups
    out = []
    for item in grouped:
        if type(item) is OptionalityGroup:
            if item.count < 2:
                # If we have fewer than two members, we just append
                # the members. Addition allows for the empty list edge
                # case to work.
                out += item.members
                continue
        out.append(item)
    return out


def get_kind_from_str(db_name):
    from attachments.kinds import ATTACHMENTS, OtherAttachment

    kinds = {kind.db_name: kind for kind in ATTACHMENTS}
    try:
        return kinds[db_name]
    except KeyError:
        return OtherAttachment
