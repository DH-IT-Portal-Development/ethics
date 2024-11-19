from django.utils.translation import gettext as _
from django.urls import reverse

from main.utils import renderable
from proposals.models import Proposal


# The following is a copy of the DocItem class from
# documents_list.py. I prefer to copy it here so that we
# can in the future just delete said file entirely
# without thinking about it too much.


class DocItem:
    """
    Provides a consistent interface to items in an AttachmentsList
    """

    def __init__(self, name, **kwargs):
        self.name = name
        self.filename = None
        self.link_url = None
        self.field = None
        self.sets_content_disposition = False

        self.__dict__.update(kwargs)

    def get_filename(self):
        if self.filename:
            return self.filename
        return self.field.name

    def get_link_url(self):
        if self.link_url:
            return self.link_url
        return self.field.url


class AttachmentItem(DocItem):
    """
    A wrapper for AttachmentsList items that works with Attachment slots.
    """

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


class Container:
    """
    A simple container class that serves as a header for AttachmentsList
    categories.
    """

    def __init__(self, header, **kwargs):
        self.header = header
        self.items = []
        self.order = 0
        self.__dict__.update(kwargs)


class DocList(list):
    """
    A list-like of attachments that can output its contents as containers
    separated per attached objects.
    """

    def __init__(self, *args, proposal=None, **kwargs,):
        if not proposal:
            return RuntimeError(
                "No proposal provided to DocList",
            )
        self.proposal = proposal
        return super().__init__(*args, **kwargs)

    def as_containers(self):
        """
        Return all slots contained within as a nice dictionary with headers.
        """
        containers = []
        # The proposal container must always show up and is handled separately
        proposal_container = self.make_proposal_container(self.proposal)
        containers.append(proposal_container)
        per_item = self.per_item()
        for item in per_item.keys():
            if type(item) is Proposal:
                container = proposal_container
            else:
                # This must be a Study object
                container = Container(_("Traject {}").format(item.order))
                container.order = 200 + item.order
            container.items += [self.make_docitem(slot) for slot in per_item[item]]
            containers.append(container)
        return sorted(containers, key=lambda c: c.order)

    def per_item(self):
        """
        Sorts all the slots into a dict with their owner object
        as the key.
        """
        items = set([slot.attached_object for slot in self])
        item_dict = {item: [] for item in items}
        for slot in self:
            item_dict[slot.attached_object].append(slot)
        return item_dict

    def make_proposal_container(self, proposal):
        """
        The proposal header needs custom entries that are not Attachment
        models. The custom logic for that lives here.
        """
        container = Container(_("Aanvraag"))
        container.order = 100
        # The proposal PDF isn't an attachment, so we add it manually
        proposal_pdf = DocItem(_("Aanvraag in PDF-vorm"))
        proposal_pdf.link_url = reverse("proposals:pdf", args=(proposal.pk,))
        container.items.append(proposal_pdf)
        # Pre-approval
        if proposal.pre_approval_pdf:
            pre_approval = DocItem(_("Eerdere goedkeuring"))
            pre_approval.field = proposal.pre_approval_pdf
            container.items.append(pre_approval)

        # Pre-assessment
        if proposal.pre_assessment_pdf:
            pre_assessment = DocItem(_("Aanvraag bij voortoetsing"))
            pre_assessment.field = proposal.pre_assessment_pdf

            container.items.append(pre_assessment)

        # WMO
        if (
            hasattr(proposal, "wmo")
            and proposal.wmo.status == proposal.wmo.WMOStatuses.JUDGED
        ):
            metc_decision = DocItem(_("Beslissing METC"))
            metc_decision.field = proposal.wmo.metc_decision_pdf

            container.items.append(metc_decision)
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
        review,
        request=None,
    ):
        self.review = review
        self.proposal = review.proposal
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
            proposal=self.proposal,
        ).as_containers()
        return containers

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["review"] = self.review
        context["proposal"] = self.proposal
        context["containers"] = self.containers
        return context
