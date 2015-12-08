from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.views.generic.detail import SingleObjectMixin

from .models import Proposal, Task

SECRETARY = 'Secretaris'
COMMISSION = 'Commissie'


class LoginRequiredMixin(object):
    """Mixin for generic views to retun to login view if not logged in"""
    @classmethod
    def as_view(cls, **initkwargs):
        view = super(LoginRequiredMixin, cls).as_view(**initkwargs)
        return login_required(view)


class UserAllowedMixin(SingleObjectMixin):
    def get_object(self, queryset=None):
        """
        Checks whether the current User is:
        - in the 'SECRETARY' or 'COMMISSION' group
        - an applicant of this proposal
        - a supervisor of this proposal
        If not, a PermissionDenied is raised.
        """
        obj = super(UserAllowedMixin, self).get_object(queryset)

        if isinstance(obj, Proposal):
            proposal = obj
        elif isinstance(obj, Task):
            proposal = obj.session.proposal
        else:
            proposal = obj.proposal

        allowed_users = get_user_model().objects.filter(groups__name=SECRETARY)
        allowed_users |= get_user_model().objects.filter(groups__name=COMMISSION)
        allowed_users |= proposal.applicants.all()
        allowed_users |= get_user_model().objects.filter(pk=proposal.supervisor)
        print allowed_users

        if self.request.user not in allowed_users:
            raise PermissionDenied

        return obj
