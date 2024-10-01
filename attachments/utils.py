from django.template.loader import get_template
from django.utils.translation import gettext as _

from attachments.kinds import ATTACHMENTS
from attachments.models import Attachment

class Renderable:

    template_name = None

    def get_template_name(self,):
        return self.template_name

    def get_context_data(self,):
        return {}

    def render(self, context):
        context = context.flatten()
        context.update(self.get_context_data())
        template = get_template(self.get_template_name())
        return template.render(context)

class AttachmentContainer(
        Renderable
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
