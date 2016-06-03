from django.core.exceptions import PermissionDenied
from django.views.generic.detail import SingleObjectMixin

from .models import Review, Decision
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


class AutoReviewMixin(object):
    def get_context_data(self, **kwargs):
        """Adds the results of the machine-wise review to the context."""
        context = super(AutoReviewMixin, self).get_context_data(**kwargs)
        reasons = auto_review(self.get_object().proposal)
        context['auto_review_go'] = len(reasons) == 0
        context['auto_review_reasons'] = reasons
        return context
