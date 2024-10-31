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


class AttachmentItem(DocItem):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.attachment = self.slot.attachment.get_correct_submodel()

    @property
    def new(self,):
        return not self.attachment.parent

    @property
    def comparable(self):
        if not self.attachment.parent:
            return False
        ancestor_proposal = self.slot.get_proposal().parent
        if not ancestor_proposal:
            return False
        direct_ancestors = [ancestor_proposal] + list(ancestor_proposal.study_set.all())
        parent_attachment = self.attachment.parent.get_correct_submodel()
        if set(parent_attachment.attached_to.all()) & set(direct_ancestors):
            return True

    @property
    def compare_url(
        self,
    ):
        return reverse(
            "proposals:compare_attachments",
            kwargs={
                "proposal_pk": self.slot.get_proposal().pk,
                "old_pk": self.attachment.parent.pk,
                "new_pk": self.attachment.pk,
            },
        )

    @property
    def attachment(
        self,
    ):
        return self.slot.attachment.get_correct_submodel()

    def get_link_url(
        self,
    ):
        return self.slot.attachment.get_download_url(
            self.slot.get_proposal(),
        )

    def get_filename(
        self,
    ):
        return self.attachment.upload.original_filename


class DocList(list):
    """
    A list-like of attachments that can output its contents as containers
    separated per attached objects.
    """

    def as_containers(self):
        containers = []
        per_item = self.per_item()
        for item in per_item.keys():
            if type(item) is Proposal:
                container = self.make_proposal_container(item)
            else:
                # This must be a Study object
                container = Container(_("Traject {}").format(item.order))
                container.order = 200 + item.order
            container.items += [self.make_docitem(slot) for slot in per_item[item]]
            containers.append(container)
        return sorted(containers, key=lambda c: c.order)

    def per_item(self):
        items = set([slot.attached_object for slot in self])
        item_dict = {item: [] for item in items}
        for slot in self:
            item_dict[slot.attached_object].append(slot)
        return item_dict

    def make_proposal_container(self, proposal):
        container = Container(_("Aanvraag"))
        container.order = 100
        # The proposal PDF isn't an attachment, so we add it manually
        proposal_pdf = DocItem(_("Aanvraag in PDF-vorm"))
        proposal_pdf.link_url = reverse("proposals:pdf", args=(proposal.pk,))
        container.items.append(proposal_pdf)
        return container

    def make_docitem(self, slot):
        docitem = AttachmentItem(
            slot.kind.name,
            slot=slot,
        )
        return docitem


class AttachmentsList(renderable):

    template_name = "attachments/attachments_list.html"

    def __init__(
        self,
        review=None,
        proposal=None,
        request=None,
    ):
        if not (review or proposal):
            raise RuntimeError(
                "AttachmentsList needs either a review " "or a proposal."
            )
        if review:
            proposal = review.proposal
        self.proposal = proposal
        self.containers = self.get_containers()
        self.request = request

    def get_containers(
        self,
    ):
        from proposals.utils.stepper import Stepper

        stepper = Stepper(self.proposal)
        filled_slots = [slot for slot in stepper.attachment_slots if slot.attachment]
        containers = DocList(
            filled_slots,
        ).as_containers()
        return containers

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["proposal"] = self.proposal
        context["containers"] = self.containers
        if self.request:
            if is_secretary(self.request.user):
                context["attachments_edit_link"] = True
        return context


def get_kind_from_str(db_name):
    from attachments.kinds import ATTACHMENTS

    kinds = {kind.db_name: kind for kind in ATTACHMENTS}
    return kinds[db_name]
