from functools import cached_property

from django.conf import settings
from django.contrib.auth.models import Group
from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.utils.translation import gettext as _
from django.views.generic.base import ContextMixin
from django.views.generic.detail import SingleObjectMixin
from django.urls import reverse

from main.utils import is_secretary

from .models import Decision, Review
from .utils.review_utils import auto_review
from .utils import AttachmentsList


class ReviewSidebarMixin:

    def get_context_data(self, **kwargs):
        if self.model is Review:
            review = self.get_object()
        else:
            review = self.get_review()
        context = super().get_context_data(**kwargs)
        context["attachments_list"] = AttachmentsList(
            review=review,
            request=self.request,
        )
        return context


class UserAllowedToDecisionMixin(SingleObjectMixin):
    class ReviewClosed(PermissionDenied):
        """
        ReviewClosed Class

        Subclass of PermissionDenied that represents an exception indicating that a review has been closed and no further actions can be performed on it.

        This is a subclass of PermissionDenied to ensure Django handles it like that.

        """

    def handle_review_closed(self, request, exception):
        """
        Handle the case when a review is closed.

        :param self: The instance of the class.
        :param request: The request object.
        :param exception: The exception object.

        :raises: The same exception object raised by the view as a fallback
        """
        # If unhandled by the view, re-raise the exception to ensure we do not
        # continue
        raise exception

    def dispatch(self, request, *args, **kwargs):
        """
        Dispatches the request to the appropriate view method based on the object type and checks user permissions.

        :param request: The request object.
        :type request: HttpRequest
        :param args: Positional arguments passed to the view method.
        :param kwargs: Keyword arguments passed to the view method.
        :return: The response returned by the dispatched view method.
        :rtype: HttpResponse
        :raises PermissionDenied: If the current user does not have permission to access the object.
        :raises self.ReviewClosed: If the review of the object is closed and the view does not handle this exception
        :raises ImproperlyConfigured: If the mixin is used for a non-decision object.
        """
        try:
            obj = self.get_object()

            if isinstance(obj, Decision):
                reviewer = obj.reviewer
                date_end = obj.review.date_end

                if request.user != reviewer:
                    raise PermissionDenied

                if date_end:
                    raise self.ReviewClosed
            else:
                raise ImproperlyConfigured(
                    "UserAllowedToDecisionMixin used for a non-decision object!"
                )
        except self.ReviewClosed as e:
            ret = self.handle_review_closed(request, e)
            # If the handle method returns None, it deemed it fine to continue
            # as if nothing happened
            if ret is not None:
                return ret

        return super().dispatch(request, *args, **kwargs)


class UserOrSecretaryAllowedMixin(SingleObjectMixin):
    def get_object(self, queryset=None):
        """
        Checks whether the current User is a reviewer in this Review,
        as well as whether the Review is still open.
        Secretaries can make decision for each other.
        """
        obj = super(UserOrSecretaryAllowedMixin, self).get_object(queryset)
        current_user = self.request.user

        if isinstance(obj, Review):
            secretary_reviewers = obj.decision_set.filter(
                reviewer__groups__name=settings.GROUP_SECRETARY
            )
            if secretary_reviewers and is_secretary(current_user):
                return obj
            if not obj.decision_set.filter(reviewer=current_user):
                raise PermissionDenied

        if isinstance(obj, Decision):
            reviewer = obj.reviewer
            date_end = obj.review.date_end

            if date_end:
                raise PermissionDenied
            if (self.request.user != reviewer) and not (
                is_secretary(reviewer) and is_secretary(current_user)
            ):
                raise PermissionDenied

        return obj


class UsersOrGroupsAllowedMixin:
    def get_group_required(self):
        """Is overwritten to provide a dynamic list of
        groups which have access"""
        if not isinstance(self.group_required, (list, tuple)):
            self.group_required = (self.group_required,)
        return self.group_required

    def get_allowed_users(self):
        """Is overwritten to provide a dynamic list of
        users who have access."""
        if not isinstance(self.allowed_users, (list, tuple)):
            self.allowed_users = (self.allowed_users,)
        return self.allowed_users

    def check_membership(self, groups):
        """Check required group(s)"""
        if self.current_user.is_superuser:
            return True
        return set(groups).intersection(set(self.current_user_groups))

    def dispatch(self, request, *args, **kwargs):
        authorized = False
        self.current_user = request.user
        self.current_user_groups = set(
            self.current_user.groups.values_list("name", flat=True)
        )

        # Default allowed groups and users
        try:
            group_required = self.group_required
        except AttributeError:
            self.group_required = None

        try:
            allowed_users = self.allowed_users
        except AttributeError:
            self.allowed_users = None

        if self.current_user.is_authenticated:
            if self.current_user in self.get_allowed_users():
                authorized = True
            elif self.check_membership(self.get_group_required()):
                authorized = True

        if not authorized:
            raise PermissionDenied

        return super(UsersOrGroupsAllowedMixin, self).dispatch(request, *args, **kwargs)


class CommitteeMixin(ContextMixin):
    @cached_property
    def committee(self):
        group = self.kwargs.get("committee")

        return Group.objects.get(name=group)

    @cached_property
    def committee_display_name(self):
        committee = _("Algemene Kamer")

        if self.committee.name == "LK":
            committee = _("Linguïstiek Kamer")

        return committee

    def get_context_data(self, **kwargs):
        context = super(CommitteeMixin, self).get_context_data(**kwargs)

        context["committee"] = self.committee
        context["committee_name"] = self.committee_display_name

        return context


class AutoReviewMixin(object):
    def get_context_data(self, **kwargs):
        """Adds the results of the machine-wise review to the context."""
        context = super(AutoReviewMixin, self).get_context_data(**kwargs)
        reasons = auto_review(self.get_object().proposal)
        context["auto_review_go"] = len(reasons) == 0
        context["auto_review_reasons"] = reasons
        return context

class HideStepperMixin():

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if is_secretary(self.request.user):
            proposal = self.get_proposal()
            editors = (
                list(proposal.applicants.all()) +
                [ proposal.supervisor ]
            )
            if self.request.user not in editors:
                context["stepper"] = None
                context["secretary_return_link"] = reverse(
                    "reviews:detail",
                    args=[proposal.latest_review().pk],
                )
        return context
