from django.views import generic
from django import forms
from django.urls import reverse
from django import forms
from django.conf import settings
from proposals.mixins import ProposalContextMixin
from proposals.models import Proposal
from studies.models import Study
from attachments.utils import get_kind_from_str
from attachments.models import Attachment, ProposalAttachment, StudyAttachment
from main.forms import ConditionalModelForm
from cdh.core import forms as cdh_forms
from django.http import FileResponse
from attachments.kinds import ATTACHMENTS, KIND_CHOICES
from attachments.utils import AttachmentKind
from cdh.core import forms as cdh_forms
from django.utils.translation import gettext as _
from reviews.mixins import UsersOrGroupsAllowedMixin


class AttachForm(
    cdh_forms.TemplatedModelForm,
):

    class Meta:
        model = Attachment
        fields = [
            "kind",
            "upload",
            "name",
            "comments",
        ]
        widgets = {
            "kind": cdh_forms.BootstrapSelect(
                choices=KIND_CHOICES,
            )
        }

    def __init__(self, kind=None, other_object=None, extra=False, **kwargs):
        self.kind = kind
        self.other_object = other_object
        # Set the correct model based on other_object
        if type(other_object) is Proposal:
            self._meta.model = ProposalAttachment
        elif type(other_object) is Study:
            self._meta.model = StudyAttachment
        super().__init__(**kwargs)
        if kind is not None:
            del self.fields["kind"]
        else:
            self.fields["kind"].default = ("other", _("Overig bestand"))

    def save(
        self,
    ):
        if self.kind:
            self.instance.kind = self.kind.db_name
        self.instance.save()
        self.instance.attached_to.add(
            self.other_object,
        )
        return super().save()


class AttachFormView:

    model = Attachment
    form_class = AttachForm
    template_name = "proposals/attach_form.html"

    def set_upload_field_label(self, form):
        # Remind the user of what they're uploading
        upload_field = form.fields["upload"]
        kind = self.get_kind()
        if kind:
            upload_field.label += f" ({kind.name})"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["proposal"] = self.get_proposal()
        owner_object = self.get_owner_object()
        if type(owner_object) is not Proposal:
            context["study"] = self.get_owner_object()
        context["kind"] = self.get_kind()
        form = context["form"]
        self.set_upload_field_label(form)
        return context

    def get_proposal(self):
        obj = self.get_owner_object()
        if type(obj) is Proposal:
            return obj
        else:
            return obj.proposal

    def get_owner_object(self):
        owner_class = self.owner_model
        other_pk = self.kwargs.get("other_pk")
        return owner_class.objects.get(pk=other_pk)

    def get_kind(self):
        kind_str = self.kwargs.get("kind", None)
        if kind_str:
            return get_kind_from_str(kind_str)
        return None

    def get_success_url(
        self,
    ):
        return reverse(
            "proposals:attachments",
            kwargs={"pk": self.get_proposal().pk},
        )

    def get_form_kwargs(
        self,
    ):
        kwargs = super().get_form_kwargs()
        kwargs.update(
            {
                "other_object": self.get_owner_object(),
            }
        )
        kwargs["kind"] = self.get_kind()
        return kwargs


class ProposalAttachView(
    AttachFormView,
    ProposalContextMixin,
    generic.CreateView,
):

    model = Attachment
    owner_model = None
    form_class = AttachForm
    template_name = "proposals/attach_form.html"
    extra = False


class ProposalUpdateAttachmentView(
    AttachFormView,
    ProposalContextMixin,
    generic.UpdateView,
):
    model = Attachment
    form_class = AttachForm
    template_name = "proposals/attach_form.html"
    editing = True

    def get_object(
        self,
    ):
        attachment_pk = self.kwargs.get("attachment_pk")
        attachment = Attachment.objects.get(pk=attachment_pk)
        obj = attachment.get_correct_submodel()
        return obj

    def get_owner_object(self):
        instance = self.get_object().get_correct_submodel()
        attached_field = instance._meta.get_field("attached_to")
        other_class = attached_field.related_model
        other_pk = self.kwargs.get("other_pk")
        return other_class.objects.get(pk=other_pk)


class DetachForm(
    forms.Form,
):
    confirmation = forms.BooleanField()


class ProposalDetachView(
    ProposalContextMixin,
    generic.detail.SingleObjectMixin,
    generic.FormView,
):
    form_class = DetachForm
    model = Attachment
    template_name = "proposals/detach_form.html"
    pk_url_kwarg = "attachment_pk"

    def get_owner_object(
        self,
    ):
        attachment = self.get_object()
        return attachment.get_owner_for_proposal(
            self.get_proposal(),
        )

    def get_context_data(self, *args, **kwargs):
        self.object = self.get_object()
        context = super().get_context_data(*args, **kwargs)
        return context

    def get_object(
        self,
    ):
        obj = super().get_object()
        return obj.get_correct_submodel()

    def get_proposal(
        self,
    ):
        proposal_pk = self.kwargs.get("proposal_pk")
        return Proposal.objects.get(pk=proposal_pk)

    def form_valid(self, form):
        attachment = self.get_object()
        attachment.detach(self.get_owner_object())
        return super().form_valid(form)

    def get_success_url(
        self,
    ):
        return reverse(
            "proposals:attachments",
            kwargs={"pk": self.get_proposal().pk},
        )


class AttachmentDetailView(
    generic.DetailView,
):
    template_name = "proposals/attachment_detail.html"
    model = Attachment


class ProposalAttachmentsView(
    ProposalContextMixin,
    generic.DetailView,
):

    template_name = "proposals/attachments.html"
    model = Proposal

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_slots = self.get_stepper().attachment_slots
        proposal_slots = [
            slot for slot in all_slots if type(slot.attached_object) is Proposal
        ]
        study_slots = {}
        for study in self.get_proposal().study_set.all():
            study_slots[study] = []
        for slot in all_slots:
            if type(slot.attached_object) is Study:
                study_slots[slot.attached_object].append(slot)
        context["study_slots"] = study_slots
        context["proposal_slots"] = proposal_slots
        return context


class ProposalAttachmentDownloadView(
    UsersOrGroupsAllowedMixin,
    generic.View,
):
    original_filename = False

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        self.original_filename = kwargs.pop("original_filename", False)
        super().__init__(*args, **kwargs)

    def get(
        self,
        request,
        proposal_pk,
        attachment_pk,
    ):
        self.attachment = Attachment.objects.get(
            pk=attachment_pk,
        )
        return self.get_file_response()

    def get_filename(self):
        if self.original_filename:
            return self.attachment.upload.original_filename
        else:
            return self.get_filename_from_kind()

    def get_filename_from_kind(self):
        self.kind = AttachmentKind.from_proposal(
            self.proposal,
            self.attachment,
        )
        return self.kind.name

    def get_file_response(self):
        attachment_file = self.attachment.upload.file
        return FileResponse(
            attachment_file,
            filename=self.get_filename(),
            as_attachment=True,
        )

    def get_allowed_users(self):

        self.proposal = Proposal.objects.get(
            pk=self.kwargs.get("proposal_pk"),
        )
        allowed_users = list(self.proposal.applicants.all())
        if self.proposal.supervisor:
            allowed_users.append(self.proposal.supervisor)
        return allowed_users

    def get_group_required(self):
        group_required = [
            settings.GROUP_SECRETARY,
            settings.GROUP_CHAIR,
        ]
        if self.proposal.reviewing_committee.name == "AK":
            group_required += [settings.GROUP_GENERAL_CHAMBER]
        if self.proposal.reviewing_committee.name == "LK":
            group_required += [settings.GROUP_LINGUISTICS_CHAMBER]

        return group_required
