from proposals.models import Proposal
from django.utils.translation import ugettext as _
from django.urls import reverse
from django.conf import settings
from django.utils.safestring import mark_safe

class ReviewActions:


    def __init__(self, review):

        self.review = review

        # Create and initialize actions
        self.detail_actions = [UnsubmitReview(review)]
        self.ufl_actions = []

        self.all_actions = self.ufl_actions + self.detail_actions

    def __call__(self, user):

        return self.get_all_actions(user)

    def get_all_actions(self, user):

        return [a for a in self.all_actions if a.is_available(user)]

    def get_ufl_actions(self, user):

        return [a for a in self.ufl_actions if a.is_available(user)]

    def get_detail_actions(self, user):

        return [a for a in self.detail_actions if a.is_available(user)]


class ReviewAction:

    def __init__(self, review, user=None):

        self.review = review
        self.user = user

    def is_available(user=None):
        '''Returns true if this action is available to the specified
        user given the current review.'''

        if not user:
            user = self.user

        # Defaults to always available
        return True

    def action_url(self, user=None):
        '''Returns a URL for the action'''

        return '#'

    def text_with_link(self, user=None):

        return '<a href="{}">{}</a>'.format(self.action_url(),
                                            self.description(),
        )

    def description(self):

        return 'description or name for {} not defined'.format(self.__name__)

    def __str__(self):

        return mark_safe(self.text_with_link())


class UnsubmitReview(ReviewAction):

    def is_available(self, user):
        '''Only allow secretary to unsubmit'''

        user_groups = user.groups.values_list("name", flat=True)
        if settings.GROUP_SECRETARY in user_groups:
            return True
        else:
            return False

    def action_url(self, user=None):

        return reverse('reviews:unsubmit', args=(self.review.proposal.pk,))

    def description(self):

        return _('Beëindig de beoordeling van deze studie')
