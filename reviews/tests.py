from datetime import datetime

from django.conf import settings
from django.contrib.auth.models import User, Group
from django.test import TestCase

from .models import Review, Decision
from .utils import start_review, auto_review, auto_review_observation, auto_review_task
from core.models import YES, DOUBT
from proposals.models import Proposal, Relation
from proposals.utils import generate_ref_number
from studies.models import Study, Compensation, AgeGroup
from observations.models import Observation
from tasks.models import Session, Task, Registration, RegistrationKind


class BaseReviewTestCase(TestCase):
    fixtures = ['relations', 'compensations', 'registrations', 'registrationkinds', 'agegroups', 'groups']

    def setUp(self):
        """
        Sets up the Users and a default Proposal to use in the tests below.
        """
        self.secretary = User.objects.create_user('secretary', 'test@test.com', 'secret')
        self.c1 = User.objects.create_user('c1', 'test@test.com', 'secret')
        self.c2 = User.objects.create_user('c2', 'test@test.com', 'secret')
        self.user = User.objects.create_user('user', 'test@test.com', 'secret')
        self.supervisor = User.objects.create_user('supervisor', 'test@test.com', 'secret')

        self.secretary.groups.add(Group.objects.get(name=settings.GROUP_SECRETARY))
        self.c1.groups.add(Group.objects.get(name=settings.GROUP_COMMISSION))
        self.c2.groups.add(Group.objects.get(name=settings.GROUP_COMMISSION))

        self.proposal = Proposal.objects.create(title='p1', reference_number=generate_ref_number(self.user),
                                                date_start=datetime.now(),
                                                created_by=self.user, supervisor=self.supervisor,
                                                relation=Relation.objects.get(pk=4))
        self.study = Study.objects.create(proposal=self.proposal, order=1, compensation=Compensation.objects.get(pk=2))


class ReviewTestCase(BaseReviewTestCase):
    def test_start_review(self):
        """
        Tests starting of a Review from a submitted Proposal.
        """
        # If the Relation on a Proposal requires a supervisor, a Review for the supervisor should be started.
        review = start_review(self.proposal)
        self.assertEqual(review.stage, Review.SUPERVISOR)
        self.assertEqual(Decision.objects.filter(reviewer=self.supervisor).count(), 1)
        self.assertEqual(Decision.objects.filter(review=review).count(), 1)
        self.assertEqual(review.decision_set.count(), 1)

        # If the Relation on a Proposal does not require a supervisor, a assignment review should be started.
        self.proposal.relation = Relation.objects.get(pk=5)
        self.proposal.save()
        review = start_review(self.proposal)
        self.assertEqual(review.stage, Review.ASSIGNMENT)
        self.assertEqual(Decision.objects.filter(reviewer=self.secretary).count(), 1)
        self.assertEqual(Decision.objects.filter(review=review).count(), 1)
        self.assertEqual(review.decision_set.count(), 1)


class SupervisorTestCase(BaseReviewTestCase):
    def test_decision_supervisor(self):
        """
        Tests whether a Decision from the supervisor leads to a change in the Review.
        """
        review = start_review(self.proposal)
        self.assertEqual(review.go, None)

        decision = Decision.objects.filter(review=review)[0]
        decision.go = Decision.APPROVED
        decision.save()
        review.refresh_from_db()
        self.assertEqual(review.go, True)


class AssignmentTestCase(BaseReviewTestCase):
    def test_assignment(self):
        """
        Tests whether the assignment works correctly.
        """
        pass


class CommissionTestCase(BaseReviewTestCase):
    def test_decision_commission(self):
        """
        Tests whether the commission phase in a Review works correctly.
        """
        # Set the relation to a supervisor so we can skip the first phase
        self.proposal.relation = Relation.objects.get(pk=5)
        self.proposal.save()
        review = start_review(self.proposal)
        self.assertEqual(review.stage, Review.ASSIGNMENT)
        self.assertEqual(review.go, None)

        # Create a Decision for a member of the commission group
        Decision.objects.create(review=review, reviewer=self.c1)
        review.stage = Review.COMMISSION
        review.refresh_from_db()

        decisions = Decision.objects.filter(review=review)
        self.assertEqual(len(decisions), 2)

        decisions[0].go = Decision.APPROVED
        decisions[0].save()
        review.refresh_from_db()
        self.assertEqual(review.go, None)  # undecided

        decisions[1].go = Decision.NOT_APPROVED
        decisions[1].save()
        review.refresh_from_db()
        self.assertEqual(review.go, False)  # no go

        decisions[1].go = Decision.APPROVED
        decisions[1].save()
        review.refresh_from_db()
        self.assertEqual(review.go, True)  # go


class AutoReviewTests(BaseReviewTestCase):
    def test_auto_review(self):
        reasons = auto_review(self.proposal)
        self.assertEqual(len(reasons), 0)

        self.study.has_intervention = True
        self.study.save()

        reasons = auto_review(self.proposal)
        self.assertEqual(len(reasons), 1)

        self.study.legally_incapable = True
        self.study.save()

        reasons = auto_review(self.proposal)
        self.assertEqual(len(reasons), 2)

        self.study.passive_consent = True
        self.study.save()

        reasons = auto_review(self.proposal)
        self.assertEqual(len(reasons), 3)

        self.study.deception = DOUBT
        self.study.save()

        reasons = auto_review(self.proposal)
        self.assertEqual(len(reasons), 4)

        self.study.has_traits = True
        self.study.save()

        reasons = auto_review(self.proposal)
        self.assertEqual(len(reasons), 5)

        self.study.sessions_number = 2
        self.study.save()

        reasons = auto_review(self.proposal)
        self.assertEqual(len(reasons), 6)

        self.study.stressful = YES
        self.study.save()

        reasons = auto_review(self.proposal)
        self.assertEqual(len(reasons), 7)

        self.study.risk = YES
        self.study.save()

        reasons = auto_review(self.proposal)
        self.assertEqual(len(reasons), 8)

    def test_auto_review_age_groups(self):
        self.study.has_sessions = True
        self.study.age_groups = AgeGroup.objects.filter(pk=2)  # toddlers
        self.study.save()

        s1 = Session.objects.create(study=self.study, order=1, tasks_number=2)
        s1_t1 = Task.objects.create(session=s1, order=1, duration=20)
        s1_t2 = Task.objects.create(session=s1, order=2, duration=20)
        self.study.save()

        self.assertEqual(s1.net_duration(), 40)

        reasons = auto_review(self.proposal)
        self.assertEqual(len(reasons), 0)

        s1_t2.duration = 30
        s1_t2.save()
        self.study.save()
        self.assertEqual(s1.net_duration(), 50)

        reasons = auto_review(self.proposal)
        self.assertEqual(len(reasons), 1)

    def test_auto_review_observation(self):
        self.study.has_observation = True
        self.study.save()
        o = Observation.objects.create(study=self.study, days=1, mean_hours=1)

        reasons = auto_review(self.proposal)
        self.assertEqual(len(reasons), 0)

        self.study.observation.is_nonpublic_space = True
        self.study.observation.has_advanced_consent = False
        self.study.observation.save()

        reasons = auto_review_observation(o)
        self.assertEqual(len(reasons), 1)

        self.study.observation.is_anonymous = True
        self.study.observation.save()

        reasons = auto_review_observation(o)
        self.assertEqual(len(reasons), 2)

    def test_auto_review_task(self):
        self.study.has_sessions = True
        self.study.age_groups = AgeGroup.objects.filter(pk=4)  # adolescents
        self.study.save()

        reasons = auto_review(self.proposal)
        self.assertEqual(len(reasons), 0)

        s1 = Session.objects.create(study=self.study, order=1, tasks_number=1)
        s1_t1 = Task.objects.create(session=s1, order=1)
        s1_t1.registrations = Registration.objects.filter(pk=6)  # psychofysiological measurements

        reasons = auto_review_task(self.study, s1_t1)
        self.assertEqual(len(reasons), 1)

        s1_t1.registration_kinds = RegistrationKind.objects.filter(requires_review=True)  # psychofysiological measurements / other
        s1_t1.save()

        reasons = auto_review_task(self.study, s1_t1)
        self.assertEqual(len(reasons), 2)
