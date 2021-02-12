from datetime import date
from collections import OrderedDict

from braces.views import GroupRequiredMixin, LoginRequiredMixin
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone
from django.views import generic
from django.utils.translation import ugettext_lazy as _

from main.utils import get_reviewers, get_secretary, is_secretary
from proposals.models import Proposal
from .forms import (DecisionForm, ReviewAssignForm, ReviewCloseForm,
                    ChangeChamberForm)
from .mixins import (AutoReviewMixin, UserAllowedMixin,
                     CommitteeMixin, UserOrSecretaryAllowedMixin,
                     UsersOrGroupsAllowedMixin)
from .models import Decision, Review
from .utils import notify_secretary, start_review_route


class DecisionListView(GroupRequiredMixin, CommitteeMixin, generic.ListView):
    context_object_name = 'decisions'
    template_name = 'reviews/decision_list.html'
    group_required = [
        settings.GROUP_SECRETARY,
        settings.GROUP_GENERAL_CHAMBER,
        settings.GROUP_LINGUISTICS_CHAMBER,
    ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['title'] = _("Mijn besluiten")

        return context

    def get_queryset(self):
        """Returns all open Decisions of the current User"""

        if is_secretary(self.request.user):
            return self.get_queryset_for_secretary()

        return self.get_queryset_for_committee()


    def get_queryset_for_committee(self):
        """Returns all open Decisions of the current User"""
        decisions = OrderedDict()

        objects = Decision.objects.filter(
            reviewer=self.request.user,
            review__proposal__reviewing_committee=self.committee
        )

        for obj in objects:
            proposal = obj.review.proposal

            if proposal.pk not in decisions:
                decisions[proposal.pk] = obj
            else:
                if decisions[proposal.pk].pk < obj.pk:
                    decisions[proposal.pk] = obj

        return [value for key, value in decisions.items()]

    def get_queryset_for_secretary(self):
        """Returns all open Decisions of the current User"""
        decisions = OrderedDict()
        # Decision-for-secretary-exists cache.
        dfse_cache = {}

        objects = Decision.objects.filter(
            reviewer__groups__name=settings.GROUP_SECRETARY,
            review__proposal__reviewing_committee=self.committee
        ).order_by('-review__proposal__date_created')

        for obj in objects:
            proposal = obj.review.proposal

            if proposal.pk not in dfse_cache:
                dfse_cache[proposal.pk] = Decision.objects.filter(
                    review__proposal=proposal,
                    reviewer=self.request.user
                ).exists()

            # If there is a decision for this user, but this decision isn't
            # for this user, skip!
            # The template handles adding a different button for creating
            # a new decision for a secretary that doesn't have one yet.
            if dfse_cache[proposal.pk] and obj.reviewer != self.request.user:
                continue

            if proposal.pk not in decisions:
                decisions[proposal.pk] = obj
            else:
                if decisions[proposal.pk].pk < obj.pk:
                    decisions[proposal.pk] = obj
        
        
        return [decisions[k] for k in decisions.keys()]


class DecisionMyOpenView(GroupRequiredMixin, CommitteeMixin, generic.ListView):
    context_object_name = 'decisions'
    template_name = 'reviews/decision_list.html'
    group_required = [
        settings.GROUP_SECRETARY,
        settings.GROUP_GENERAL_CHAMBER,
        settings.GROUP_LINGUISTICS_CHAMBER,
    ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['title'] = _("Mijn openstaande besluiten")

        return context

    def get_queryset(self):
        """Returns all open Decisions of the current User"""

        if is_secretary(self.request.user):
            return self.get_queryset_for_secretary()

        return self.get_queryset_for_committee()


    def get_queryset_for_committee(self):
        """Returns all open Decisions of the current User"""
        decisions = OrderedDict()

        objects = Decision.objects.filter(
            reviewer=self.request.user,
            go='',
            review__proposal__reviewing_committee=self.committee
        ).order_by('review__proposal__date_created')

        for obj in objects:
            proposal = obj.review.proposal

            if proposal.pk not in decisions:
                decisions[proposal.pk] = obj
            else:
                if decisions[proposal.pk].pk < obj.pk:
                    decisions[proposal.pk] = obj

        return [value for key, value in decisions.items()]

    def get_queryset_for_secretary(self):
        """Returns all open Decisions of the current User"""
        decisions = OrderedDict()
        # Decision-for-secretary-exists cache.
        dfse_cache = {}

        objects = Decision.objects.filter(
            reviewer__groups__name=settings.GROUP_SECRETARY,
            go='',
            review__proposal__reviewing_committee=self.committee
        ).order_by('-review__proposal__date_created')

        for obj in objects:
            proposal = obj.review.proposal

            if proposal.pk not in dfse_cache:
                dfse_cache[proposal.pk] = Decision.objects.filter(
                    review__proposal=proposal,
                    reviewer=self.request.user
                ).exists()

            # If there is a decision for this user, but this decision isn't
            # for this user, skip!
            # The template handles adding a different button for creating
            # a new decision for a secretary that doesn't have one yet.
            if dfse_cache[proposal.pk] and obj.reviewer != self.request.user:
                continue

            if proposal.pk not in decisions:
                decisions[proposal.pk] = obj
            else:
                if decisions[proposal.pk].pk < obj.pk:
                    decisions[proposal.pk] = obj

        return [value for key, value in decisions.items()]


class DecisionOpenView(GroupRequiredMixin, CommitteeMixin, generic.ListView):
    context_object_name = 'decisions'
    template_name = 'reviews/decision_list_open.html'
    group_required = settings.GROUP_SECRETARY

    def get_queryset(self):
        """Returns all open Committee Decisions of all Users"""
        decisions = OrderedDict()
        # Decision-for-secretary-exists cache.
        dfse_cache = {}

        objects = Decision.objects.filter(
            go='',
            review__proposal__reviewing_committee=self.committee
        ).order_by('-review__proposal__date_created'
            ).exclude(review__stage=Review.SUPERVISOR)

        for obj in objects:
            proposal = obj.review.proposal

            if proposal.pk not in dfse_cache:
                dfse_cache[proposal.pk] = Decision.objects.filter(
                    review__proposal=proposal,
                    reviewer=self.request.user
                ).exists()

            # If there is a decision for this user, but this decision isn't
            # for this user, skip!
            # The template handles adding a different button for creating
            # a new decision for a secretary that doesn't have one yet.
            if dfse_cache[proposal.pk] and obj.reviewer != self.request.user:
                continue

            if proposal.pk not in decisions:
                decisions[proposal.pk] = obj
            else:
                if decisions[proposal.pk].pk < obj.pk:
                    decisions[proposal.pk] = obj

        return [value for key, value in decisions.items()]


class ToConcludeProposalView(GroupRequiredMixin, CommitteeMixin,
                             generic.ListView):
    context_object_name = 'reviews'
    template_name = 'reviews/review_list.html'
    group_required = settings.GROUP_SECRETARY

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['title'] = _("Nog af te handelen studies")

        return context

    def get_queryset(self):
        """Returns all open Committee Decisions of all Users"""
        reviews = {}
        objects = Review.objects.filter(
            stage__gte=Review.CLOSING,
            proposal__status__gte=Proposal.SUBMITTED,
            proposal__date_confirmed=None,
            proposal__reviewing_committee=self.committee,
        ).filter(
            Q(continuation=Review.GO) |
            Q(continuation=Review.GO_POST_HOC) |
            Q(continuation=None)
        ).order_by('-proposal__date_created')

        for obj in objects:
            proposal = obj.proposal
            if proposal.pk not in reviews:
                reviews[proposal.pk] = obj
            else:
                if reviews[proposal.pk].pk < obj.pk:
                    reviews[proposal.pk] = obj

        return [value for key, value in reviews.items()]


class AllProposalReviewsView(UsersOrGroupsAllowedMixin,
                             CommitteeMixin, generic.ListView):
    context_object_name = 'reviews'
    template_name = 'reviews/review_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['title'] = _("Alle ingezonden studies")

        return context
    
    def get_group_required(self):
        # Depending on committee kwarg we test for the correct group
        
        group_required = [settings.GROUP_SECRETARY]
        
        if self.committee.name == 'AK':
            group_required += [ settings.GROUP_GENERAL_CHAMBER ]
        if self.committee.name == 'LK':
            group_required += [ settings.GROUP_LINGUISTICS_CHAMBER ]
        
        return group_required
    
    def get_queryset(self):
        """Returns all open Committee Decisions of all Users"""
        reviews = OrderedDict()
        objects = Review.objects.filter(
            stage__gte=Review.ASSIGNMENT,
            proposal__status__gte=Proposal.SUBMITTED,
            proposal__reviewing_committee=self.committee,
        ).order_by('-proposal__date_created')

        for obj in objects:
            proposal = obj.proposal
            if proposal.pk not in reviews:
                reviews[proposal.pk] = obj
            else:
                if reviews[proposal.pk].pk < obj.pk:
                    reviews[proposal.pk] = obj
        

        return [value for key, value in reviews.items()]


class SupervisorDecisionOpenView(GroupRequiredMixin, CommitteeMixin,
                                 generic.ListView):
    """
    This page displays all proposals to be reviewed by supervisors. Not to be
    confused with SupervisorView, which displays all open reviews for a specific
     supervisor. Viewable for the secretary only!
    """
    context_object_name = 'decisions'
    template_name = 'reviews/decision_supervisor_list_open.html'
    group_required = settings.GROUP_SECRETARY

    def get_queryset(self):
        """Returns all studies that still need conclusion actions by the
        secretary
        """
        objects = Decision.objects.filter(
            go='',
            review__stage=Review.SUPERVISOR,
            review__proposal__status=Proposal.SUBMITTED_TO_SUPERVISOR,
            review__proposal__reviewing_committee=self.committee
        ).order_by('-review__proposal__date_created')
        
        decisions = OrderedDict()

        for obj in objects:
            proposal = obj.review.proposal
            if proposal.pk not in decisions:
                decisions[proposal.pk] = obj
            else:
                if decisions[proposal.pk].pk < obj.pk:
                    decisions[proposal.pk] = obj

        return [value for key, value in decisions.items()]


class SupervisorView(LoginRequiredMixin, generic.ListView):
    """
        This page displays all proposals to be reviewed by a specific
        supervisors. Not to be confused with SupervisorDecisionOpenView, which
        displays all open reviews for all supervisors.
        """
    context_object_name = 'decisions'

    def get_queryset(self):
        """Returns all the current open Decisions for the current User"""
        objects = Decision.objects.filter(
            review__date_end=None,
            review__stage=Review.SUPERVISOR,
            reviewer=self.request.user
            ).order_by('-review__proposal__date_created')
        decisions = OrderedDict

        for obj in objects:
            proposal = obj.review.proposal
            if proposal.pk not in decisions:
                decisions[proposal.pk] = obj
            else:
                if decisions[proposal.pk].pk < obj.pk:
                    decisions[proposal.pk] = obj

        return [value for key, value in decisions.items()]


class ReviewDetailView(LoginRequiredMixin, AutoReviewMixin,
                       UsersOrGroupsAllowedMixin, generic.DetailView):
    """
    Shows the Decisions for a Review
    """
    model = Review
    
    def get_group_required(self):
        
        obj = self.get_object()
        group_required = [ settings.GROUP_SECRETARY, obj.proposal.reviewing_committee.name ]
        
        return group_required


class ChangeChamberView(LoginRequiredMixin, UserAllowedMixin,
                        generic.UpdateView):
    model = Proposal
    form_class = ChangeChamberForm
    template_name = 'reviews/change_chamber_form.html'

    def get_success_url(self):
        committee = self.object.reviewing_committee.name
        return reverse('reviews:my_open', args=[committee])


class ReviewAssignView(GroupRequiredMixin, AutoReviewMixin, generic.UpdateView):
    """
    Allows a User of the SECRETARY group to assign reviewers.
    """
    model = Review
    form_class = ReviewAssignForm
    template_name = 'reviews/review_assign_form.html'
    group_required = settings.GROUP_SECRETARY

    def get_success_url(self):
        committee = self.object.proposal.reviewing_committee.name
        return reverse('reviews:my_open', args=[committee])

    def form_valid(self, form):
        """Updates the Review stage and start the selected Review route for the selected Users."""
        route = form.instance.short_route
        review = self.object

        if route is not None:
            # Start a short/long route
            form.instance.stage = Review.COMMISSION

            current_reviewers = set(review.current_reviewers())
            selected_reviewers = set(form.cleaned_data['reviewers'])
            new_reviewers = selected_reviewers - current_reviewers
            obsolete_reviewers = current_reviewers - selected_reviewers

            # Set the proper end date
            # It should be 2 weeks for short_routes
            if route and form.instance.date_should_end is None:
                form.instance.date_should_end = timezone.now() + \
                    timezone.timedelta(
                    weeks=settings.SHORT_ROUTE_WEEKS
                )
            elif form.instance.date_should_end is not None:
                # We have no desired end date for long track reviews
                form.instance.date_should_end = None

            # Create a new Decision for new reviewers
            start_review_route(form.instance, new_reviewers, route)

            # Remove the Decision for obsolete reviewers
            Decision.objects.filter(review=review,
                                    reviewer__in=obsolete_reviewers).delete()
            
            # Finally, update the review process
            # This prevents it waiting for removed reviewers
            review.update_go()
            
        else:
            # Directly mark this Proposal as closed: applicants should start a revision Proposal
            for decision in Decision.objects.filter(review=review):
                decision.go = Decision.NEEDS_REVISION
                decision.date_decision = timezone.now()
                decision.save()

            # Mark the proposal as finished
            proposal = form.instance.proposal
            proposal.status = Proposal.DECISION_MADE
            proposal.status_review = False
            proposal.date_reviewed = timezone.now()
            proposal.save()

            form.instance.continuation = Review.REVISION
            form.instance.date_end = timezone.now()
            form.instance.stage = Review.CLOSED

        return super(ReviewAssignView, self).form_valid(form)


class ReviewCloseView(GroupRequiredMixin, generic.UpdateView):
    model = Review
    form_class = ReviewCloseForm
    template_name = 'reviews/review_close_form.html'
    group_required = settings.GROUP_SECRETARY

    def get_success_url(self):
        committee = self.object.proposal.reviewing_committee.name
        return reverse('reviews:my_archive', args=[committee])

    def get_form_kwargs(self):
        """
        Adds allow_long_route_continuation to the form_kwargs.
        The long route continuation is only allowed for short route Reviews
        that are not of preliminary assessment Proposals.
        """
        review = self.get_object()

        kwargs = super(ReviewCloseView, self).get_form_kwargs()
        kwargs[
            'allow_long_route_continuation'] = review.short_route and not review.proposal.is_pre_assessment
        return kwargs

    def get_initial(self):
        """
        Set initial values:
        - continuation to GO if review was positive
        - in_archive to True as long as we are not dealing with preliminary assessment
        """
        review = self.get_object()

        initial = super(ReviewCloseView, self).get_initial()
        initial['continuation'] = Review.GO if review.go else Review.NO_GO

        if review.proposal.date_start and \
           review.proposal.date_start < date.today():
            initial['continuation'] = \
                Review.GO_POST_HOC if initial['continuation'] == Review.GO \
                else Review.NO_GO_POST_HOC

        initial['in_archive'] = not review.proposal.is_pre_assessment
        return initial

    def form_valid(self, form):
        proposal = form.instance.proposal

        if form.instance.continuation in [
            Review.GO, Review.NO_GO, Review.GO_POST_HOC, Review.NO_GO_POST_HOC
        ]:
            proposal.status = Proposal.DECISION_MADE
            proposal.status_review = form.instance.continuation in [
                Review.GO, Review.GO_POST_HOC
            ]
            proposal.date_reviewed = timezone.now()
            proposal.save()
        elif form.instance.continuation == Review.LONG_ROUTE:
            # Create a new review
            review = Review.objects.create(
                proposal=proposal,
                stage=Review.COMMISSION,
                short_route=False,
                date_start=timezone.now())
            # Create a Decision for the secretary
            Decision.objects.create(review=review, reviewer=get_secretary())
            # Start the long review route
            start_review_route(review, get_reviewers(), False)
        elif form.instance.continuation == Review.METC:
            proposal.status = Proposal.DRAFT
            proposal.save()
            proposal.wmo.enforced_by_commission = True
            proposal.wmo.save()

        proposal.in_archive = form.cleaned_data['in_archive']
        proposal.has_minor_revision = form.cleaned_data['has_minor_revision']
        proposal.minor_revision_description = form.cleaned_data[
            'minor_revision_description']
        proposal.save()

        form.instance.stage = Review.CLOSED

        return super(ReviewCloseView, self).form_valid(form)


class CreateDecisionRedirectView(LoginRequiredMixin,
                                 GroupRequiredMixin,
                                 generic.RedirectView):
    """
    This redirect first creates a new decision for a secretary that does not
    have one yet, and redirects to the DecisionUpdateView
    """
    group_required = settings.GROUP_SECRETARY

    def get_redirect_url(self, *args, **kwargs):
        review_pk = kwargs.get('review', None)
        decision_pk = None

        if not review_pk:
            raise PermissionDenied

        existing_decision_qs = Decision.objects.filter(
            reviewer=self.request.user,
            review_id=review_pk
        )

        # Re-use an existing one if present
        if existing_decision_qs.exists():
            decision_pk = existing_decision_qs.last()
        else:
            decision = Decision.objects.create(
                reviewer=self.request.user,
                review_id=review_pk,
            )
            decision_pk = decision.pk


        return reverse('reviews:decide', args=[decision_pk])

class DecisionUpdateView(LoginRequiredMixin, UserAllowedMixin,
                         generic.UpdateView):
    """
    Allows a User to make a Decision on a Review.
    """
    model = Decision
    form_class = DecisionForm

    def is_reviewer(self):
        if self.request.user.is_superuser:
            return True
        user_groups = self.request.user.groups.values_list("name", flat=True)
        return {settings.GROUP_SECRETARY, settings.GROUP_LINGUISTICS_CHAMBER,
                settings.GROUP_GENERAL_CHAMBER
                }.intersection(set(user_groups))

    def get_success_url(self):
        if self.is_reviewer():
            committee = self.object.review.proposal.reviewing_committee.name
            return reverse('reviews:my_archive', args=[committee])
        else:
            return reverse('proposals:my_archive')

    def form_valid(self, form):
        """Save the decision date and send e-mail to secretary"""
        form.instance.date_decision = timezone.now()
        notify_secretary(form.instance)
        return super(DecisionUpdateView, self).form_valid(form)
