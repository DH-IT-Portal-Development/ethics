from django.views import generic
from django import forms
from django.urls import reverse
from proposals.mixins import ProposalContextMixin
from proposals.models import Proposal
from studies.models import Study
from attachments.kinds import ProposalAttachments, get_kind_from_str
from attachments.models import Attachment, ProposalAttachment, StudyAttachment
from main.forms import ConditionalModelForm
from cdh.core import forms as cdh_forms
from django.http import FileResponse
from attachments.kinds import ATTACHMENTS, AttachmentKind


class AttachForm(
        cdh_forms.TemplatedModelForm,
):

    class Meta:
        model = Attachment
        fields = [
            "upload",
            "name",
            "comments",
        ]

    def __init__(self, kind=None, other_object=None, **kwargs):
        self.kind = kind
        self.other_object = other_object
        # Set the correct model based on other_object
        if type(other_object) is Proposal:
            self._meta.model = ProposalAttachment
        elif type(other_object) is Study:
            self._meta.model = StudyAttachment
        return super().__init__(**kwargs)

    def save(self,):
        self.instance.kind = self.kind.db_name
        self.instance.save()
        self.instance.attached_to.add(
            self.other_object,
        )
        return super().save()


class ProposalAttachView(
        ProposalContextMixin,
        generic.CreateView,
):

    model = Attachment
    form_class = AttachForm
    template_name = "proposals/attach_form.html"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def set_upload_field_label(self, form):
        # Remind the user of what they're uploading
        upload_field = form.fields["upload"]
        kind = self.get_kind()
        upload_field.label += f" ({kind.name})"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["proposal"] = self.get_proposal()
        owner_object = self.get_owner_object()
        if type(owner_object) is not Proposal:
            context["study"] = self.get_owner_object()
        context["kind"] = self.get_kind()
        context["kind_name"] = self.get_kind().name
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
        owner_model = self.get_kind().attached_object
        return owner_model.objects.get(pk=self.kwargs.get("other_pk"))

    def get_kind(self):
        kind_str = self.kwargs.get("kind")
        return get_kind_from_str(kind_str)

    def get_success_url(self,):
        return reverse(
            "proposals:attachments",
            kwargs={"pk": self.get_proposal().pk},
        )

    def get_form_kwargs(self,):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            "kind": self.get_kind(),
            "other_object": self.get_owner_object(),
        })
        return kwargs

class ProposalUpdateAttachmentView(
        ProposalContextMixin,
        generic.UpdateView,
):
    model = Attachment
    form_class = AttachForm
    template_name = "proposals/attach_form.html"

    def get_proposal(self):
        obj = self.get_owner_object()
        if type(obj) is Proposal:
            return obj
        else:
            return obj.proposal

    def get_owner_object(self):
        owner_model = self.get_kind().attached_object
        return owner_model.objects.get(pk=self.kwargs.get("other_pk"))

    def get_kind(self):
        kind_str = self.kwargs.get("kind")
        return get_kind_from_str(kind_str)



class ProposalAttachmentsView(
        ProposalContextMixin,
        generic.DetailView,
):

    template_name = "proposals/attachments.html"
    model = Proposal

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        manager = ProposalAttachments(
            self.get_proposal(),
        )
        context["manager"] = manager

        context["study_slots"] = manager.study_slots

        return context


class ProposalAttachmentDownloadView(
        generic.View,
):
    original_filename = False

    def __init__(self, *args, **kwargs,):
        self.original_filename = kwargs.pop("original_filename", False)
        super().__init__(*args, **kwargs)

    def get(self, request, proposal_pk, attachment_pk,):
        self.attachment = Attachment.objects.get(
            pk=attachment_pk,
        )
        self.proposal = Proposal.objects.get(
            pk=self.kwargs.get("proposal_pk"),
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
