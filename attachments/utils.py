from django.template.loader import get_template
from django.utils.translation import gettext as _
from django.urls import reverse

from main.utils import renderable
from proposals.models import Proposal

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

    def get_instances_for_object(self):
        manager = getattr(self.owner, self.attached_field)
        return manager.filter(kind=self.db_name)

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


class ProposalAttachments:
    """
    """

    def __init__(self, proposal):
        self.proposal = proposal
        self.proposal_kinds = self.walk_proposal()
        self.study_kinds = self.walk_all_studies()
        self.match_slots()

    def match_slots(self,):
        self.proposal_slots = []
        for kind in self.proposal_kinds:
            self.proposal_slots += kind.get_slots(manager=self)
        self.study_slots = {}
        for study, kinds in self.study_kinds.items():
            self.study_slots[study] = []
            for kind in kinds:
                self.study_slots[study] += kind.get_slots(manager=self)

    def walk_proposal(self):
        kinds = []
        for kind in PROPOSAL_ATTACHMENTS:
            kinds.append(
                kind(self.proposal),
            )
        return kinds

    def walk_all_studies(self):
        study_dict = {}
        for study in self.proposal.study_set.all():
            study_dict[study] = self.walk_study(study)
        return study_dict

    def walk_study(self, study):
        kinds = []
        for kind in STUDY_ATTACHMENTS:
            kinds.append(
                kind(study),
            )
        return kinds


class AttachmentContainer(
        renderable,
):
    outer_css_classes = []
    template_name = "attachments/base_single_attachment.html"

    def __init__(self, attachment, proposal=None):
        self.proposal = proposal
        self.attachment = attachment

    def get_outer_css_classes(self,):
        classes = self.outer_css_classes
        if self.is_active:
            classes += ["attachment-active"]
        return " ".join(classes)

    def get_context_data(self):
        return {
            "ac": self,
            "proposal": self.proposal,
        }

    @property
    def is_from_previous_proposal(self,):
        if not self.proposal.parent:
            return False
        pp = self.proposal.parent
        return self.attachment in pp.attachments_set.all()

    @property
    def is_revised_file(self,):
        if not all(
            self.attachment.parent,
            self.proposal.parent,
        ):
            return False
        pa = self.attachment.parent
        pp = self.proposal.parent
        return pa in pp.attachments_set.all()

    @property
    def is_brand_new(self,):
        if self.attachment.parent:
            return False
        return True

    def get_origin_display(self):
        if not self.attachment.upload:
            return _("Nog toe te voegen")
        if self.is_from_previous_proposal:
            return _("Van vorige revisie")
        if self.is_revised_file:
            return _("Nieuwe versie")
        if self.is_brand_new:
            return _("Nieuw aangeleverd bestand")
        return _("Herkomst onbekend")

    @property
    def is_active(self):
        if not self.proposal:
            return True
        return self.proposal in self.attachment.attached_to.all()


class ProposalAttachments():

    def __init__(self, proposal):

        # Setup
        self.proposal = proposal
        from attachments.kinds import ATTACHMENTS
        self.available_kinds = ATTACHMENTS

        # Populate lists
        self.all_attachments = self._populate()

    def _populate(self,):
        # These are the Attachments that actually exist
        self.provided = self._fetch()
        # These are the Attachments that are still required
        # (we create placeholders for them)
        self.complement = self._complement_all()
        return self.provided + self.complement

    def _fetch(self,):
        qs = self.proposal.attachments.all()
        return list(qs)

    def _provided_of_kind(self, kind,):
        out = filter(
            lambda a: a.kind == kind.db_name,
            self.provided,
        )
        return list(out)

    def _complement_of_kind(self, kind,):
        required = kind.num_required(self.proposal)
        provided = len(self._provided_of_kind(kind))
        for i in range(required - provided):
            new_attachment = Attachment()
            new_attachment.kind = kind.db_name
            self.complement.append(new_attachment)

    def _complement_all(self,):
        self.complement = []
        for kind in self.available_kinds:
            self._complement_of_kind(kind)
        return self.complement

    def as_containers(self,):
        return [
            AttachmentContainer(a, proposal=self.propsal)
            for a in self.all_attachments
        ]


class AttachmentSlot(renderable):

    template_name = "attachments/slot.html"

    def __init__(self, kind, attached_object, attachment=None, manager=None):
        self.kind = kind
        self.attachment = attachment
        self.desiredness = _("Verplicht")
        self.manager = manager

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["slot"] = self
        return context

    def get_attach_url(self,):
        return self.kind.get_attach_url()

    def get_delete_url(self,):
        return "#"

    def get_edit_url(self,):
        return reverse(
            "proposals:update_attachment",
            kwargs={
                "attachment_pk": self.attachment.pk,
                "proposal_pk": self.manager.proposal.pk,
            }
        )

def get_kind_from_str(db_name):
    from attachments.kinds import ATTACHMENTS
    kinds = {
        kind.db_name: kind
        for kind in ATTACHMENTS
    }
    return kinds[db_name]
