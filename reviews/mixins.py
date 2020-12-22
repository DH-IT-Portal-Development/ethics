from django.conf import settings
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied
from django.utils.functional import cached_property
from django.utils.translation import ugettext as _
from django.views.generic.base import ContextMixin
from django.views.generic.detail import SingleObjectMixin

from main.utils import is_secretary

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
            secretary_reviewers = obj.decision_set.filter(reviewer__groups__name=settings.GROUP_SECRETARY)
            if secretary_reviewers and is_secretary(current_user):
                return obj
            if not obj.decision_set.filter(reviewer=current_user):
                raise PermissionDenied

        if isinstance(obj, Decision):
            reviewer = obj.reviewer
            date_end = obj.review.date_end

            if date_end:
                raise PermissionDenied
            if (self.request.user != reviewer) and \
                    not (is_secretary(reviewer) and is_secretary(current_user)):
                raise PermissionDenied

        return obj


class UsersOrGroupsAllowedMixin():

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
        """ Check required group(s) """
        if self.current_user.is_superuser:
            return True
        return set(groups).intersection(set(self.current_user_groups))

    def dispatch(self, request, *args, **kwargs):
        authorized = False
        self.current_user = request.user
        self.current_user_groups = set(self.current_user.groups.values_list("name", flat=True))
        
        # Default allowed groups and users        
        try: group_required = self.group_required
        except AttributeError:
            self.group_required = None
        
        try: allowed_users = self.allowed_users
        except AttributeError:
            self.allowed_users = None
        
        if self.current_user.is_authenticated:
            if self.current_user in self.get_allowed_users():
                authorized = True
            elif self.check_membership(self.get_group_required()):
                authorized = True

        if not authorized:
            raise PermissionDenied

        return super(UsersOrGroupsAllowedMixin, self).dispatch(
            request, *args, **kwargs)
    


class CommitteeMixin(ContextMixin):

    @cached_property
    def committee(self):
        group = self.kwargs.get('committee')

        return Group.objects.get(name=group)

    @cached_property
    def committee_display_name(self):
        committee = _('Algemene Kamer')

        if self.committee.name == 'LK':
            committee = _('Linguïstiek Kamer')

        return committee

    def get_context_data(self, **kwargs):
        context = super(CommitteeMixin, self).get_context_data(**kwargs)

        context['committee'] = self.committee
        context['committee_name'] = self.committee_display_name

        return context


class AutoReviewMixin(object):
    def get_context_data(self, **kwargs):
        """Adds the results of the machine-wise review to the context."""
        context = super(AutoReviewMixin, self).get_context_data(**kwargs)
        reasons = auto_review(self.get_object().proposal)
        context['auto_review_go'] = len(reasons) == 0
        context['auto_review_reasons'] = reasons
        return context
