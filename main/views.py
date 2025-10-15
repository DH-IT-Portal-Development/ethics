# -*- encoding: utf-8 -*-
from urllib.parse import urlparse, urlunparse

import os

from braces.views import LoginRequiredMixin, GroupRequiredMixin, UserPassesTestMixin
from django.apps import apps
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.db.models import Q
from django.forms import modelformset_factory
from django.http import (
    HttpResponseRedirect,
    JsonResponse,
    FileResponse,
    Http404,
    QueryDict,
)
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.detail import SingleObjectMixin

from interventions.models import Intervention
from main.models import Faculty, SystemMessage
from main.utils import is_member_of_humanities, can_view_archive
from observations.models import Observation
from proposals.models import Proposal
from reviews.models import Review
from tasks.models import Session, Task


################
# Views
################
class _SystemMessageView(generic.ListView):
    model = SystemMessage

    def get_queryset(self):
        now = timezone.now()
        return self.model.objects.filter(not_after__gt=now, not_before__lt=now)


class SeasonalCoverImageMixin:
    seasons = {
        "spring": {
            "image": "main/images/coverimage-spring.jpg",
            "author": "Dick Boetekees",
            # This controls how the image is fitted inside the container; every image has its own 'best' fit
            "classes": "align-items-end",
        },
        "summer": {
            "image": "main/images/coverimage-summer.jpg",
            "author": "Bert Spiertz",
            "classes": "align-items-middle",
        },
        "autumn": {
            "image": "main/images/coverimage-autumn.jpg",
            "author": "Ivar Pel",
            "classes": "align-items-middle",
        },
        "winter": {
            "image": "main/images/coverimage-winter.jpg",
            "author": "Simona Evstatieva",
            "classes": "align-items-middle",
        },
    }

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["cover_image"] = self.get_seasonal_cover_image()
        return context

    def get_seasonal_cover_image(self):
        now = timezone.now()

        # Allow overriding by adding a ?season= get parameter
        # For dev/testing mostly
        if override := self.request.GET.get("season", None):
            if override in self.seasons.keys():
                return self.seasons[override]

        if now.month in [3, 4, 5]:
            return self.seasons["spring"]
        elif now.month in [6, 7, 8]:
            return self.seasons["summer"]
        elif now.month in [9, 10, 11]:
            return self.seasons["autumn"]
        else:
            return self.seasons["winter"]


class HomeView(LoginRequiredMixin, SeasonalCoverImageMixin, _SystemMessageView):
    template_name = "main/index.html"
    max_n_proposals = 2

    def no_permissions_fail(self, request=None):
        """
        Overrides normal permission fail to redirect to landing instead of
        directly to login
        """
        resolved_url = reverse("main:landing")

        return HttpResponseRedirect(f"{resolved_url}?next=/")

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        context["is_humanities"] = is_member_of_humanities(self.request.user)
        context["proposals"] = self.get_priority_proposals()
        context["can_view_archive"] = can_view_archive(self.request.user)

        return context

    def get_priority_proposals(self):
        proposals = []

        proposals += Proposal.objects.filter(
            supervisor=self.request.user,
            status=Proposal.Statuses.SUBMITTED_TO_SUPERVISOR,
            date_reviewed_supervisor=None,
        ).order_by("date_submitted_supervisor")[: self.max_n_proposals]

        if len(proposals) == self.max_n_proposals:
            return proposals

        n_needed = self.max_n_proposals - len(proposals)

        proposals += (
            Proposal.objects.filter(
                applicants=self.request.user,
                status=Proposal.Statuses.DRAFT,
            )
            .distinct()
            .order_by(
                "-date_modified",
            )[:n_needed]
        )

        if len(proposals) == self.max_n_proposals:
            return proposals

        n_needed = self.max_n_proposals - len(proposals)

        proposals += (
            Proposal.objects.filter(
                applicants=self.request.user,
                status__gt=Proposal.Statuses.DRAFT,
            )
            .distinct()
            .order_by(
                "-date_modified",
            )[:n_needed]
        )

        return proposals


class LandingView(SeasonalCoverImageMixin, _SystemMessageView):
    template_name = "main/landing.html"
    model = SystemMessage

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        context["next"] = self.request.GET.get("next", settings.LOGIN_REDIRECT_URL)
        context["saml"] = hasattr(settings, "SAML_CONFIG")
        context["show_saml"] = settings.SHOW_SAML_LOGIN
        context["show_django"] = settings.SHOW_DJANGO_LOGIN
        context["login_descriptors"] = settings.SHOW_LOGIN_DESCRIPTORS

        return context


class UserDetailView(GroupRequiredMixin, generic.DetailView):
    group_required = [
        settings.GROUP_SECRETARY,
        settings.GROUP_LINGUISTICS_CHAMBER,
        settings.GROUP_GENERAL_CHAMBER,
    ]
    model = get_user_model()
    context_object_name = "user_object"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["reviews"] = self.get_user_reviews()

        return context

    def get_user_reviews(self):
        """Returns all Committee Reviews of this user"""
        reviews = {}
        objects = Review.objects.filter(
            stage__gte=Review.Stages.ASSIGNMENT,
            proposal__status__gte=Proposal.Statuses.SUBMITTED,
            proposal__created_by=self.get_object(),
        )

        for obj in objects:
            proposal = obj.proposal
            if proposal not in reviews:
                reviews[proposal.pk] = obj
            else:
                if reviews[proposal.pk].pk < obj.pk:
                    reviews[proposal.pk] = obj

        return [value for key, value in reviews.items()]


################
# AJAX callbacks
################
@csrf_exempt
def check_requires(request):
    """
    This call checks whether a certain value requires another input to be filled.
    """
    values = map(int, request.POST.getlist("value[]"))
    model = apps.get_model(request.POST.get("app"), request.POST.get("model"))
    required_values = model.objects.filter(
        **{request.POST.get("field"): True}
    ).values_list("id", flat=True)
    result = bool(set(required_values).intersection(values))
    return JsonResponse({"result": result})


################
# Helpers
################
class AllowErrorsOnBackbuttonMixin(object):
    def form_invalid(self, form):
        """
        On back button, allow form to have errors.
        """
        if "save_back" in self.request.POST:
            return HttpResponseRedirect(self.get_back_url())
        else:
            return super(AllowErrorsOnBackbuttonMixin, self).form_invalid(form)


class FacultyRequiredMixin(UserPassesTestMixin):
    """A clone of GroupRequiredMixin, but checking faculties instead"""

    faculty_required = None

    def get_faculty_required(self):
        if self.faculty_required is None or (
            not isinstance(self.faculty_required, (list, tuple, str))
        ):
            raise ImproperlyConfigured(
                '{0} requires the "faculty_required" attribute to be set and be '
                "one of the following types: string, unicode, list or "
                "tuple".format(self.__class__.__name__)
            )
        if not isinstance(self.faculty_required, (list, tuple)):
            self.faculty_required = (self.faculty_required,)
        return self.faculty_required

    def check_membership(self, faculty):
        """Check required faculty(ies)"""
        user_faculties = self.request.user.faculties.values_list(
            "internal_name", flat=True
        )
        return set(faculty).intersection(set(user_faculties))

    def test_func(self, user):
        in_faculty = False
        if user.is_authenticated:
            in_faculty = self.check_membership(self.get_faculty_required())
        return in_faculty


class HumanitiesRequiredMixin(FacultyRequiredMixin):
    faculty_required = Faculty.InternalNames.HUMANITIES


class HumanitiesOrPrivilegeRequiredMixin(UserPassesTestMixin):
    """
    Checks for Humanities faculty affiliation, but also lets in users belonging
    to a privileged set of groups.
    """

    raise_exception = True

    def test_func(self, user):
        return can_view_archive(user)


class UserAllowedMixin(SingleObjectMixin):
    def get_object(self, queryset=None):
        """
        Allows access to a proposal based on the status of a Proposal
        and the position of the User. He can be:
        - in the 'SECRETARY', 'GENERAL_CHAMBER' or 'LINGUISTICS_CHAMBER' group
        - an applicant of this Proposal
        - a supervisor of this Proposal
        If the status of the Proposal is not in line with the status of the User,
        a PermissionDenied is raised.
        """
        obj = super(UserAllowedMixin, self).get_object(queryset)

        if isinstance(obj, Proposal):
            proposal = obj
        elif (
            isinstance(obj, Observation)
            or isinstance(obj, Intervention)
            or isinstance(obj, Session)
        ):
            proposal = obj.study.proposal
        elif isinstance(obj, Task):
            proposal = obj.session.study.proposal
        else:
            proposal = obj.proposal

        applicants = proposal.applicants.all()
        if proposal.supervisor:
            supervisor = get_user_model().objects.filter(pk=proposal.supervisor.pk)
        else:
            supervisor = get_user_model().objects.none()
        commission = get_user_model().objects.filter(
            groups__name=settings.GROUP_SECRETARY
        )
        if proposal.reviewing_committee.name == settings.GROUP_LINGUISTICS_CHAMBER:
            commission |= get_user_model().objects.filter(
                groups__name=settings.GROUP_LINGUISTICS_CHAMBER
            )
        if proposal.reviewing_committee.name == settings.GROUP_GENERAL_CHAMBER:
            commission |= get_user_model().objects.filter(
                groups__name=settings.GROUP_GENERAL_CHAMBER
            )

        if proposal.status >= Proposal.Statuses.SUBMITTED:
            if self.request.user not in commission:
                raise PermissionDenied
        elif proposal.status >= Proposal.Statuses.SUBMITTED_TO_SUPERVISOR:
            if self.request.user not in supervisor:
                raise PermissionDenied
        else:
            if (
                self.request.user not in applicants | supervisor
                and self.request.user != proposal.created_by
            ):
                raise PermissionDenied

        return obj


class FormSetUserAllowedMixin(UserAllowedMixin):
    def check_allowed(self):
        """
        Allows access to a proposal based on the status of a Proposal
        and the position of the User. He can be:
        - in the 'SECRETARY', 'LINGUISITICS_CHAMBER' or 'GENERAL_CHAMBER' group
        - an applicant of this Proposal
        - a supervisor of this Proposal
        If the status of the Proposal is not in line with the status of the User,
        a PermissionDenied is raised.
        """

        for obj in self.objects:
            if isinstance(obj, Proposal):
                proposal = obj
            elif (
                isinstance(obj, Observation)
                or isinstance(obj, Intervention)
                or isinstance(obj, Session)
            ):
                proposal = obj.study.proposal
            elif isinstance(obj, Task):
                proposal = obj.session.study.proposal
            else:
                proposal = obj.proposal

            applicants = proposal.applicants.all()
            if proposal.supervisor:
                supervisor = get_user_model().objects.filter(pk=proposal.supervisor.pk)
            else:
                supervisor = get_user_model().objects.none()
            commission = get_user_model().objects.filter(
                groups__name=settings.GROUP_SECRETARY
            )

            if proposal.reviewing_committee.name == settings.GROUP_LINGUISTICS_CHAMBER:
                commission |= get_user_model().objects.filter(
                    groups__name=settings.GROUP_LINGUISTICS_CHAMBER
                )

            if proposal.reviewing_committee.name == settings.GROUP_GENERAL_CHAMBER:
                commission |= get_user_model().objects.filter(
                    groups__name=settings.GROUP_GENERAL_CHAMBER
                )

            if proposal.status >= Proposal.Statuses.SUBMITTED:
                if self.request.user not in commission:
                    raise PermissionDenied
            elif proposal.status >= Proposal.Statuses.SUBMITTED_TO_SUPERVISOR:
                if self.request.user not in supervisor:
                    raise PermissionDenied
            else:
                if self.request.user not in applicants | supervisor:
                    raise PermissionDenied


class CreateView(LoginRequiredMixin, SuccessMessageMixin, generic.CreateView):
    """Generic create view including success message and login required
    mixins"""

    def get_success_url(self):
        """Sets the success_url based on the submit button pressed"""
        return success_url(self)


class UpdateView(
    LoginRequiredMixin, SuccessMessageMixin, UserAllowedMixin, generic.UpdateView
):
    """Generic update view including success message, user allowed and login
    required mixins"""

    def get_success_url(self):
        """Sets the success_url based on the submit button pressed"""
        return success_url(self)


class FormSetUpdateView(
    FormSetUserAllowedMixin, LoginRequiredMixin, SuccessMessageMixin, generic.View
):
    """Generic update view that uses a formset. This allows you to edit
    multiple forms of the same type on the same page.
    """

    form = None
    _formset = None
    queryset = None
    extra = 0

    def get(self, request, *args, **kwargs):
        self._on_request()
        return render(request, self.template_name, self.get_context_data())

    def post(self, request, *args, **kwargs):
        self._on_request()

        formset = self._formset(request.POST, request.FILES, queryset=self.objects)
        self.pre_validation(formset)
        if formset.is_valid():
            self.save_form(formset)
            return HttpResponseRedirect(self.get_success_url())
        else:
            return render(
                request, self.template_name, self.get_context_data(formset=formset)
            )

    def pre_validation(self, formset):
        """This method can be overridden to manipulate the formset before
        validation"""
        pass

    def save_form(self, formset):
        formset.save()

    def _on_request(self):
        self._formset = modelformset_factory(
            self.form._meta.model, form=self.form, extra=self.extra
        )
        self.objects = self.get_queryset()
        self.check_allowed()

    def get_queryset(self):
        if self.queryset is None:
            raise ImproperlyConfigured(
                "Either override get_queryset, or provide a queryset class " "variable"
            )

        return self.queryset

    def get_success_url(self):
        """Sets the success_url based on the submit button pressed"""
        return success_url(self)

    def get_context_data(self, **kwargs):
        if "view" not in kwargs:
            kwargs["view"] = self

        kwargs["objects"] = self.objects

        if "formset" not in kwargs:
            kwargs["formset"] = self._formset(queryset=self.objects)

        return kwargs


class DeleteView(LoginRequiredMixin, UserAllowedMixin, generic.DeleteView):
    """Generic delete view including login required and user allowed mixin and
    alternative for success message"""

    def form_valid(self, form):
        messages.success(self.request, self.success_message)
        return super(DeleteView, self).form_valid(form)


class UserMediaView(LoginRequiredMixin, generic.View):
    """Respond with a given user uploaded file if the request
    is logged in. Makes it so that user uploads are no longer
    public."""

    def get_response_path(self, filename):
        """Make sure the requested filename exists within MEDIA_ROOT,
        to prevent upwards directory traversal."""
        media_root = os.path.realpath(settings.MEDIA_ROOT)
        filepath = os.path.realpath(
            os.path.join(media_root, filename),
        )
        if not os.path.commonpath([filepath, media_root]) == media_root:
            raise Http404
        else:
            return filepath

    def get_response_file(self, filename):
        filepath = self.get_response_path(filename)
        try:
            f = open(filepath, "rb")
            return f
        except FileNotFoundError:
            raise Http404

    def get(self, request, filename):
        return FileResponse(
            self.get_response_file(filename),
            filename=filename,
            as_attachment=True,
        )


def success_url(self):
    if "next" in self.request.GET:
        return self.request.GET["next"]
    if "save_continue" in self.request.POST:
        return self.get_next_url()
    if "save_back" in self.request.POST:
        return self.get_back_url()
    else:
        return reverse("proposals:my_archive")
