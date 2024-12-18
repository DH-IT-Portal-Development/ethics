import mimetypes

from django.template.loader import get_template
from django.utils.translation import gettext as _
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
            self.optionality_group.members.append(self)

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
    def is_new(self):
        ancestor_proposal = self.get_proposal().parent
        # If this is a fresh proposal we must be new, regardless
        # of if we have a parent.
        if not ancestor_proposal:
            return True
        # Otherwise, we're new only if we have no parent.
        return not self.attachment.parent

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

def attachment_filename_generator(file):
    from attachments.kinds import ProposalAttachment, StudyAttachment

    #try to get a Proposal attachment, otherwise, it must be a Study attachment
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
    from attachments.kinds import ATTACHMENTS, OtherAttachment

    kinds = {kind.db_name: kind for kind in ATTACHMENTS}
    try:
        kind = kinds[db_name]
        return kind
    except KeyError:
        return OtherAttachment
