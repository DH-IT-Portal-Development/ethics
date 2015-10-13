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
        Checks whether the current User is in the applicants of a Proposal
        and whether the Proposal has not yet been submitted.
        """
        obj = super(UserAllowedMixin, self).get_object(queryset)

        applicants = []
        status = None
        if isinstance(obj, Proposal):
            applicants = obj.applicants.all()
            status = obj.status
        elif isinstance(obj, Task):
            applicants = obj.session.proposal.applicants.all()
            status = obj.session.proposal.status
        else:
            applicants = obj.proposal.applicants.all()
            status = obj.proposal.status

        if self.request.user not in applicants or status >= Proposal.SUBMITTED_TO_SUPERVISOR:
            raise PermissionDenied

        return obj
