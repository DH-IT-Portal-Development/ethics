from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.views.generic.detail import SingleObjectMixin

from .models import Review, Decision


class LoginRequiredMixin(object):
    """
    Mixin for generic views to retun to login view if not logged in
    TODO: this is the same as that in the proposals application.
    """
    @classmethod
    def as_view(cls, **initkwargs):
        view = super(LoginRequiredMixin, cls).as_view(**initkwargs)
        return login_required(view)


class UserAllowedMixin(SingleObjectMixin):
    def get_object(self, queryset=None):
        """
        Checks whether the current User is a reviewer in this Review,
        as well as whether the Review is still open.
        """
        obj = super(UserAllowedMixin, self).get_object(queryset)

        if isinstance(obj, Review):
            if not obj.decision_set.filter(reviewer=self.request.user) or obj.date_end:
                raise PermissionDenied

        if isinstance(obj, Decision):
            reviewer = obj.reviewer
            date_end = obj.review.date_end

            if self.request.user != reviewer or date_end:
                raise PermissionDenied

        return obj
