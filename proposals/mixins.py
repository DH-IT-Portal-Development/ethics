from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.views.generic.detail import SingleObjectMixin

from .models import Proposal, Observation, Intervention, Session, Task

SECRETARY = 'Secretaris'
COMMISSION = 'Commissie'


class LoginRequiredMixin(object):
    """
    Mixin for generic views to retun to login view if not logged in.
    """
    @classmethod
    def as_view(cls, **initkwargs):
        view = super(LoginRequiredMixin, cls).as_view(**initkwargs)
        return login_required(view)


class AllowErrorsMixin(object):
    def form_invalid(self, form):
        """
        On back button, allow form to have errors.
        """
        if 'save_back' in self.request.POST:
            return HttpResponseRedirect(self.get_back_url())
        else:
            return super(AllowErrorsMixin, self).form_invalid(form)


class DeletionAllowedMixin(object):
    def get_object(self, queryset=None):
        """
        Prevent deletion of a single Task/Session in a Session/Study.
        """
        obj = super(DeletionAllowedMixin, self).get_object(queryset)

        if isinstance(obj, Session):
            if obj.study.sessions_number == 1:
                raise PermissionDenied
        elif isinstance(obj, Task):
            if obj.session.tasks_number == 1:
                raise PermissionDenied

        return obj


class UserAllowedMixin(SingleObjectMixin):
    def get_object(self, queryset=None):
        """
        Allows access to a proposal based on the status of a Proposal
        and the position of the User. He can be:
        - in the 'SECRETARY' or 'COMMISSION' group
        - an applicant of this Proposal
        - a supervisor of this Proposal
        If the status of the Proposal is not in line with the status of the User,
        a PermissionDenied is raised.
        """
        obj = super(UserAllowedMixin, self).get_object(queryset)

        if isinstance(obj, Proposal):
            proposal = obj
        elif isinstance(obj, Observation) or isinstance(obj, Intervention) or isinstance(obj, Session):
            proposal = obj.study.proposal
        elif isinstance(obj, Task):
            proposal = obj.session.study.proposal
        else:
            proposal = obj.proposal

        applicants = proposal.applicants.all()
        if proposal.supervisor:
            supervisor = get_user_model().objects.filter(pk=proposal.supervisor.id)
        else:
            supervisor = get_user_model().objects.none()
        commission = get_user_model().objects.filter(groups__name=SECRETARY)
        commission |= get_user_model().objects.filter(groups__name=COMMISSION)

        if proposal.status >= Proposal.SUBMITTED:
            if self.request.user not in commission:
                raise PermissionDenied
        elif proposal.status >= Proposal.SUBMITTED_TO_SUPERVISOR:
            if self.request.user not in supervisor:
                raise PermissionDenied
        else:
            if self.request.user not in applicants | supervisor:
                raise PermissionDenied

        return obj
