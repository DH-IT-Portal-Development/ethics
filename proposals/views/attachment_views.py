from django.views import generic
from django import forms
from django.urls import reverse
from django.http import Http404
from django import forms
from django.http import Http404
from django.core.exceptions import PermissionDenied
from django.conf import settings
from main.views import UpdateView
from proposals.mixins import ProposalContextMixin
from proposals.models import Proposal, Wmo
from studies.models import Study
from attachments.utils import get_kind_from_str
from attachments.models import Attachment, ProposalAttachment, StudyAttachment
from cdh.core import forms as cdh_forms
from django.http import FileResponse
from attachments.utils import AttachmentKind
from reviews.templatetags.documents_list import get_legacy_documents, DocItem
from reviews.mixins import HideStepperMixin
from django.utils.translation import gettext as _
from attachments.kinds import ATTACHMENTS, KIND_CHOICES
from attachments.utils import AttachmentKind, merge_groups, AttachmentSlot
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

    def __init__(self, kind=None, other_object=None, **kwargs):
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
        # Set the kind if enforced by the view.
        if self.kind:
            self.instance.kind = self.kind.db_name
        # Check if we're creating a new attachment
        if self.instance._state.adding is True:
            # If we're creating, we need to save before we can
            # adjust M2M attributes.
            self.instance.save()
        else:
            # Check we're not editing an attachment that is still in use
            # by another object.
            if self.instance.attached_to.count() > 1:
                # Saving this instance might remove historical data. So
                # we create a revision.
                return self.save_revision()
        # Attach the instance to the owner object.
        self.instance.attached_to.add(
            self.other_object,
        )
        return super().save()

    def save_revision(
        self,
    ):
        # Remember the old pk
        # Adding zero creates a new copy of the integer
        old_pk = self.instance.pk + 0
        # The following means this instance will get saved under a
        # new pk, effectively creating a copy.
        self.instance.pk = None
        self.instance.id = None
        self.instance._state.adding = True
        self.instance.save()
        # Retrieve and detach it from the current other_object.
        instance_manager = type(self.instance).objects
        old_attachment = instance_manager.get(pk=old_pk)
        old_attachment.attached_to.remove(self.other_object)
        # Remove all other instances in the attached_to
        # of the copy except for the current other_object.
        self.instance.attached_to.set([self.other_object])
        # Set the old attachment as our parent.
        self.instance.parent = old_attachment
        return super().save()


class AttachFormView:

    model = Attachment
    form_class = AttachForm
    template_name = "proposals/attach_form.html"
    # The editing variable is set in the URLconf to determine
    # if we're editing an existing file or adding a new one.
    editing = True

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
        try:
            return owner_class.objects.get(pk=other_pk)
        except owner_class.DoesNotExist:
            raise Http404

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
    HideStepperMixin,
    AttachFormView,
    ProposalContextMixin,
    generic.CreateView,
):

    model = Attachment
    owner_model = None
    form_class = AttachForm
    template_name = "proposals/attach_form.html"


class ProposalUpdateAttachmentView(
    HideStepperMixin,
    AttachFormView,
    ProposalContextMixin,
    generic.UpdateView,
):
    model = Attachment
    form_class = AttachForm
    template_name = "proposals/attach_form.html"

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
    HideStepperMixin,
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


class ProposalAttachmentsForm(
    forms.ModelForm,
):
    """
    An empty form, needed to make the navigation work.
    """

    class Meta:
        model = Proposal
        fields = []


class ProposalAttachmentsView(
    HideStepperMixin,
    ProposalContextMixin,
    UpdateView,
):

    template_name = "proposals/attachments.html"
    model = Proposal
    # this form does not do anything, it's just here to make navigation work
    form_class = ProposalAttachmentsForm

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
        # Final step to merge optionality groups
        for obj, slots in study_slots.items():
            study_slots[obj] = merge_groups(slots)
        context["study_slots"] = study_slots
        context["proposal_slots"] = merge_groups(proposal_slots)
        context["legacy_documents"] = self.legacy_documents()
        return context

    def get_next_url(self):
        if self.get_proposal().is_pre_assessment:
            return reverse("proposals:submit_pre", args=(self.object.pk,))
        return reverse("proposals:translated", args=(self.object.pk,))

    def get_back_url(self):
        # Preassessments don't have data_management
        if self.get_proposal().is_pre_assessment:
            if self.get_proposal().wmo.status != Wmo.WMOStatuses.NO_WMO:
                return reverse(
                    "proposals:wmo_application_pre", args=[self.get_proposal().pk]
                )
            # If you're at this point then you must have created a WMO object
            # so it's always the update URL, and not create
            return reverse("proposals:wmo_update_pre", args=[self.get_proposal().pk])
        return reverse("proposals:data_management", args=(self.get_proposal().pk,))

    def legacy_documents(
        self,
    ):
        containers = get_legacy_documents(self.get_proposal())
        for container in containers:
            if container.items == []:
                container.items.append(
                    DocItem(
                        _("Geen bestanden gevonden"),
                    )
                )
        return containers


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
        return self.get_file_response()

    def get_filename(self):
        if self.original_filename:
            return self.get_attachment().upload.original_filename
        else:
            return self.get_filename_from_slot()

    def get_filename_from_slot(self):
        self.slot = AttachmentSlot.from_proposal(
            self.get_attachment(),
            self.get_proposal(),
        )
        return self.slot.get_fetc_filename()

    def get_file_response(self):
        attachment_file = self.get_attachment().upload.file
        return FileResponse(
            attachment_file,
            filename=self.get_filename(),
            as_attachment=True,
        )

    def get_proposal(
        self,
    ):
        if getattr(self, "proposal", None) is None:
            try:
                self.proposal = Proposal.objects.get(
                    pk=self.kwargs.get("proposal_pk"),
                )
            except Proposal.DoesNotExist:
                raise Http404
        return self.proposal

    def get_attachment(
        self,
    ):
        if getattr(self, "attachment", None) is None:
            try:
                self.attachment = Attachment.objects.get(
                    pk=self.kwargs.get("attachment_pk"),
                ).get_correct_submodel()
            except Attachment.DoesNotExist:
                raise Http404
        else:
            # Skip relation check if the attachment is already set
            return self.attachment
        # Check attachment-proposal relation
        if not self.attachment.get_owner_for_proposal(
            self.get_proposal(),
        ):
            # This attachment doesn't belong to the given proposal,
            # so we can't check its permissions.
            raise PermissionDenied
        return self.attachment

    def get_allowed_users(self):
        proposal = self.get_proposal()
        allowed_users = list(proposal.applicants.all())
        if proposal.supervisor:
            allowed_users.append(proposal.supervisor)
        return allowed_users

    def get_group_required(self):
        proposal = self.get_proposal()
        group_required = [
            settings.GROUP_SECRETARY,
            settings.GROUP_CHAIR,
        ]
        if proposal.reviewing_committee.name == "AK":
            group_required += [settings.GROUP_GENERAL_CHAMBER]
        if proposal.reviewing_committee.name == "LK":
            group_required += [settings.GROUP_LINGUISTICS_CHAMBER]

        return group_required
