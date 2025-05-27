import mimetypes
from collections import Counter

from django.template.loader import get_template
from django.utils.translation import gettext_lazy as _
from django.urls import reverse

from main.utils import renderable, is_secretary
from proposals.models import Proposal
from studies.models import Study
from reviews.templatetags.documents_list import Container, DocItem


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
    model_document_link = "" #optional

    @classmethod
    def get_fn_part(cls):
        if hasattr(cls, "fn_part"):
            return cls.fn_part
        # Capitalize DB name
        parts = cls.db_name.split("_")
        return "-".join([part.capitalize() for part in parts])


class AttachmentSlot(renderable):

    template_name = "attachments/slot.html"

    def __init__(
        self,
        attached_object,
        attachment=None,
        kind=None,
        force_desiredness=None,
        optionality_group=None,
        order=None,
    ):
        self.attachment = attachment
        self.attached_object = attached_object
        self.order = order

        if attachment and not kind:
            # If an attachment was provided but no kind,
            # attempt to get the kind from the attachment
            self.kind = self.get_kind_from_attachment()
        else:
            self.kind = kind

        self.force_desiredness = force_desiredness
        self.optionality_group = optionality_group
        if self.optionality_group:
            self.optionality_group.members.append(self)

    @classmethod
    def from_proposal(cls, attachment, proposal):
        attached_object = attachment.get_owner_for_proposal(proposal)
        return AttachmentSlot(
            attached_object,
            attachment=attachment,
        )

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

    def get_kind_from_attachment(
        self,
    ):
        return get_kind_from_str(self.attachment.kind)

    def get_fetc_filename(
        self,
    ):
        return generate_filename(self)

    def get_provision(
        self,
    ):
        if self.comparable:
            return _("Gereviseerd")
        if self.is_new:
            return _("Nieuw bij deze aanvraag")
        return "Bestaand bestand"

    @property
    def classes(self):
        if self.required:
            if self.attachment:
                return "border-success"
            else:
                return "border-warning"
        return ""

    @property
    def is_new(self):
        """
        Returns true if this attachment file has not been seen before
        by the Ethics committee. Please note that this includes revised
        files.
        """
        ancestor_proposal = self.get_proposal().parent
        # If this is a fresh proposal we must be new, regardless
        # of if we have a parent.
        if not ancestor_proposal:
            return True
        # We gather the set of ancestor objects
        ancestor_objects = [ancestor_proposal] + list(ancestor_proposal.study_set.all())
        for obj in ancestor_objects:
            # If this object is attached to any of these ancestor objects,
            # it is definitely not new
            if self.attachment.attached_to.contains(obj):
                return False
        # If none of the above has returned yet, we consider the remaining
        # attachments to be new.
        return True

    @property
    def comparable(self):
        # No parent, no comparison
        if not self.attachment.parent:
            return False
        # If this is a new proposal, no comparison
        ancestor_proposal = self.get_proposal().parent
        if not ancestor_proposal:
            return False
        # Only if we have a parent and it's a direct ancestor, i.e. the current
        # attachment hasn't been seen by the committee before, do we return True
        direct_ancestors = [ancestor_proposal] + list(ancestor_proposal.study_set.all())
        parent_attachment = self.attachment.parent.get_correct_submodel()
        if set(parent_attachment.attached_to.all()) & set(direct_ancestors):
            return True
        return False

    @property
    def compare_url(
        self,
    ):
        if not self.comparable:
            return False
        return reverse(
            "proposals:compare_attachments",
            kwargs={
                "proposal_pk": self.get_proposal().pk,
                "old_pk": self.attachment.parent.pk,
                "new_pk": self.attachment.pk,
            },
        )

    @property
    def desiredness(self):
        if self.optionality_group:
            if not self.attachment:
                return self.optionality_group.empty_desiredness
            else:
                return self.optionality_group.filled_desiredness
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

    def get_proposal(
        self,
    ):
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

    def __init__(
        self,
    ):
        self.members = []

    @property
    def count(
        self,
    ):
        return len(self.members)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["group"] = self
        return context

    @property
    def any_slot_filled(
        self,
    ):
        for slot in self.members:
            if slot.attachment:
                return True
        return False

    @property
    def filled_desiredness(
        self,
    ):
        # Desiredness for a slot in this group if it has an attachment
        return desiredness.REQUIRED

    @property
    def empty_desiredness(
        self,
    ):
        # Desiredness for a slot in this group if it has no attachment
        if self.any_slot_filled:
            return desiredness.OPTIONAL
        else:
            return desiredness.REQUIRED


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
                out += list(item.members)
                continue
        out.append(item)
    return out


def generate_filename(slot):

    proposal = slot.get_proposal()
    chamber = proposal.reviewing_committee.name
    lastname = proposal.created_by.last_name
    refnum = proposal.reference_number
    original_fn = slot.attachment.upload.original_filename
    kind = slot.kind.get_fn_part()
    order = slot.order

    extension = (
        "." + original_fn.split(".")[-1][-7:]
    )  # At most 7 chars seems reasonable

    trajectory = None
    if not type(slot.attached_object) is Proposal:
        trajectory = "T" + str(slot.attached_object.order)

    fn_parts = [
        "FETC",
        chamber,
        refnum,
        lastname,
        trajectory,
        kind,
        order,
    ]

    # Translations will trip up join(), so we convert them here.
    # This will also remove parts that are None.
    fn_parts = [str(p) for p in fn_parts if p]

    return "-".join(fn_parts) + extension


def enumerate_slots(slots):
    """
    Provides an order attribute to all attachment slots whose kind
    appears more than once in the provided list.
    """
    # Create seperate slot lists per attached_object
    per_ao = sort_into_dict(
        slots,
        lambda x: x.attached_object,
    ).values()
    # Assign orders to them separately
    for ao_slots in per_ao:
        assign_orders(ao_slots)


def sort_into_dict(iterable, key_func):
    """
    Split iterable into separate lists in a dict whose keys
    are the shared response to all its items' key_func(item).
    """
    out_dict = {}
    for item in iterable:
        key = key_func(item)
        if key not in out_dict:
            out_dict[key] = [item]
        else:
            out_dict[key].append(item)
    return out_dict


def assign_orders(slots):
    # Count total kind occurrences
    totals = Counter([slot.kind for slot in slots])
    # Create counter to increment gradually
    kind_counter = Counter()
    # Loop through the slots
    for slot in slots:
        if totals[slot.kind] < 2:
            # Skip slots with unique kinds
            continue
        kind_counter[slot.kind] += 1
        slot.order = kind_counter[slot.kind]


def get_kind_from_str(db_name):
    from attachments.kinds import ATTACHMENTS, OtherAttachment

    kinds = {kind.db_name: kind for kind in ATTACHMENTS}
    try:
        kind = kinds[db_name]
        return kind
    except KeyError:
        return OtherAttachment
