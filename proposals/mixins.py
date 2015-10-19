from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.views.generic.detail import SingleObjectMixin

from .models import Proposal, Task


class LoginRequiredMixin(object):
    """Mixin for generic views to retun to login view if not logged in"""
    @classmethod
    def as_view(cls, **initkwargs):
        view = super(LoginRequiredMixin, cls).as_view(**initkwargs)
        return login_required(view)


class UserAllowedMixin(SingleObjectMixin):
    def get_object(self, queryset=None):
        """
        Checks whether the current User is in the applicants of a Proposal.
        """
        obj = super(UserAllowedMixin, self).get_object(queryset)

        applicants = []
        if isinstance(obj, Proposal):
            applicants = obj.applicants.all()
        elif isinstance(obj, Task):
            applicants = obj.session.proposal.applicants.all()
        else:
            applicants = obj.proposal.applicants.all()

        if self.request.user not in applicants:
            raise PermissionDenied

        return obj
