from django.utils.translation import ugettext as _
from django.urls import reverse
from django.conf import settings
from django.utils.safestring import mark_safe

from proposals.models import Proposal
from reviews.models import Review, Decision

class ReviewActions:


    def __init__(self, review, user):

        self.review = review
        self.user = user

        # Create and initialize actions
        self.detail_actions = [CloseReview(review, user),
                               DecideAction(review, user),
                               ChangeAssignment(review, user),
                               DiscontinueReview(review, user),
                               HideReview(review, user),
                               SendConfirmation(review, user),
        ]
        self.ufl_actions = []

        # Does not check for uniqueness
        self.all_actions = self.ufl_actions + self.detail_actions

    def __call__(self):

        return self.get_all_actions()

    def get_all_actions(self):

        return [a for a in self.all_actions if a.is_available()]

    def get_ufl_actions(self):

        return [a for a in self.ufl_actions if a.is_available()]

    def get_detail_actions(self):

        return [a for a in self.detail_actions if a.is_available()]


class ReviewAction:

    def __init__(self, review, user):

        self.review = review
        self. user = user

    def is_available(self, user=None):
        '''Returns true if this action is available to the specified
        user given the current review.'''

        if not user:
            user = self.user

        # Defaults to always available
        return True

    def action_url(self, user=None):
        '''Returns a URL for the action'''

        if not user:
            user = self.user

        return '#'

    def text_with_link(self, user=None):

        return '<a href="{}">{}</a>'.format(self.action_url(),
                                            self.description(),
        )

    def description(self):

        return 'description or name for {} not defined'.format(self.__name__)

    def __str__(self):

        return mark_safe(self.text_with_link())


class DecideAction(ReviewAction):

    def get_available_decision(self):
        '''Return an available decision for the current user, or None'''

        user = self.user
        review = self.review

        if review.stage != review.COMMISSION:
            return False

        try:
            decision = Decision.objects.get(review=review,
                                            reviewer=user,
                                            go='',
            )
        except Decision.DoesNotExist:
            return None

        return decision


    def is_available(self):

        review = self.review

        if not self.get_available_decision():
            return False

        return True

    def action_url(self):

        decision_pk = self.get_available_decision().pk

        return reverse('reviews:decide', args=(decision_pk,))

    def description(self):

        decision = self.get_available_decision()

        return _('Geef jouw beslissing en/of commentaar door')


class CloseReview(ReviewAction):

    def is_available(self):
        '''Only secretaries may close reviews, which must be in the
        closing stage '''

        review = self.review

        if review.stage != review.CLOSING:
            return False

        user_groups = self.user.groups.values_list("name", flat=True)
        if not settings.GROUP_SECRETARY in user_groups:
            return False

        return True

    def action_url(self):

        return reverse('reviews:close', args=(self.review.pk,))

    def description(self):

        return _('Deze aanvraag afsluiten')


class DiscontinueReview(ReviewAction):

    def is_available(self):
        '''Only allow secretaries to discontinue reviews which have
        not yet been discontinued or have been confirmed'''

        review = self.review
        user = self.user

        user_groups = user.groups.values_list("name", flat=True)
        if not settings.GROUP_SECRETARY in user_groups:
            return False

        if review.continuation in [review.DISCONTINUED,
                                   review.GO,
                                   review.GO_POST_HOC,
                                   ]:
            return False

        return True

    def action_url(self, user=None):

        return reverse('reviews:discontinue', args=(self.review.pk,))

    def description(self):

        return _('Beëindig definitief de afhandeling van deze aanvraag')


class ChangeAssignment(ReviewAction):

    def is_available(self):
        '''Only the secretary should be able to assign reviewers,
        supervisor reviews should be excluded, and no final decision
        should yet have been made.'''

        user = self.user

        user_groups = user.groups.values_list("name", flat=True)
        if not settings.GROUP_SECRETARY in user_groups:
            return False

        if self.review.stage not in [Review.REVISION,
                                     Review.NO_GO,
                                     Review.CLOSING,
                                     ]:
            return False

        return True

    def action_url(self):

        return reverse('reviews:assign', args=(self.review.pk,))

    def description(self):

        return _('Verander aangestelde commissieleden')

'''
I need to create 2 (or 3?) classes with the ReviewAction parent class:
    - One for sending a confirmation letter and changing the confirmation date
    - One for hiding the review from archive

They need to have an is available function, which performs the
checks to see whether an action should be available. 
This will be the most important.

I then need to have a function which returns the url and one which returns the
description. This is pretty straightforward.

'''

class HideReview(ReviewAction):

    def is_available(self):

        user = self.user
        review = self.review

        user_groups = user.groups.values_list("name", flat=True)
        if not settings.GROUP_SECRETARY in user_groups:
            return False
        
        if review.proposal.public == False:
            return False
        
        if review.proposal.status < Proposal.DECISION_MADE:
            return False

        return True
    
    def action_url(self):

        return reverse('proposals:archive_hide', args=(self.review.proposal.pk,))

    def description(self):

        return _('Verberg aanvraag uit het archief')
    
class SendConfirmation(ReviewAction):

    def is_available(self):

        user = self.user
        review = self.review

        user_groups = user.groups.values_list("name", flat=True)
        if not settings.GROUP_SECRETARY in user_groups:
            return False
        
        if review.stage < review.CLOSED:
            return False
        
        if not review.continuation in [review.GO, review.GO_POST_HOC]:
            return False
        
        return True
    
    def action_url(self):

        return reverse('proposals:confirmation', args=(self.review.pk,))
    
    def description(self):
        send_letter = _('Bevestigingsbrief versturen')
        change_date = _('Datum van bevestigingsbrief aanpassen')
        return send_letter if self.review.proposal.date_confirmed is None else change_date
    
    '''
    the action url function can be the same for both scenarios, but in the description,
    It would be nice to have a conditional, which checks for the review.proposal.date_confirmed attribute,
    to see whether it should be 'send confirmation letter' or 'change date'
    '''
        
# "review.proposal.date_confirmed" = change date
# see reviews/templates/reviews/vue_templates/review_list.html, line 80

