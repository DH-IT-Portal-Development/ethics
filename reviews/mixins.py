from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied
from django.utils.functional import cached_property
from django.views.generic.base import ContextMixin
from django.views.generic.detail import SingleObjectMixin

from .models import Decision, Review
from .utils import auto_review


class UserAllowedMixin(SingleObjectMixin):
    def get_object(self, queryset=None):
        """
        Checks whether the current User is a reviewer in this Review,
        as well as whether the Review is still open.
        """
        obj = super(UserAllowedMixin, self).get_object(queryset)

        if isinstance(obj, Review):
            if not obj.decision_set.filter(reviewer=self.request.user):
                raise PermissionDenied

        if isinstance(obj, Decision):
            reviewer = obj.reviewer
            date_end = obj.review.date_end

            if self.request.user != reviewer or date_end:
                raise PermissionDenied

        return obj


class CommitteeMixin(ContextMixin):

    @cached_property
    def committee(self):
        group = self.kwargs.get('committee')

        return Group.objects.get(name=group)

    def get_context_data(self, **kwargs):
        context = super(CommitteeMixin, self).get_context_data(**kwargs)

        context['committee'] = self.committee

        return context


class AutoReviewMixin(object):
    def get_context_data(self, **kwargs):
        """Adds the results of the machine-wise review to the context."""
        context = super(AutoReviewMixin, self).get_context_data(**kwargs)
        reasons = auto_review(self.get_object().proposal)
        context['auto_review_go'] = len(reasons) == 0
        context['auto_review_reasons'] = reasons
        return context
