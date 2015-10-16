from django.test import TestCase
from django.contrib.auth.models import User

from .models import Review, Decision, start_review
from proposals.models import Proposal, Relation
from proposals.utils import generate_ref_number


class ReviewTestCase(TestCase):
    fixtures = ['relations']

    def setUp(self):
        self.user = User.objects.create_user(username='test0101', email='test@test.com', password='secret', is_staff=True)
        self.supervisor = User.objects.create_user(username='supervisor', email='test@test.com', password='secret', is_staff=True)
        self.p1 = Proposal.objects.create(title='p1', reference_number=generate_ref_number(self.user),
            created_by=self.user, supervisor=supervisor, relation=Relation.objects.get(pk=4))
        self.p1 = Proposal.objects.create(title='p2', reference_number=generate_ref_number(self.user),
            created_by=self.user, supervisor=supervisor, relation=Relation.objects.get(pk=5))

    def startReviewTest(self):
        start_review(self.p1)
        review = Review.objects.filter(proposal=self.p1)[0]
        self.assertEqual(review.stage, Review.SUPERVISOR)
        self.assertEqual(Decision.objects.filter(reviewer=self.supervisor), 1)
        self.assertEqual(Decision.objects.filter(review=review), 1)

        start_review(self.p2)
        review = Review.objects.filter(proposal=self.p2)[0]
        self.assertEqual(review.stage, Review.COMMISSION)
        self.assertEqual(Decision.objects.filter(reviewer=self.user), 1)
        self.assertEqual(Decision.objects.filter(reviewer=self.supervisor), 1)
        self.assertEqual(Decision.objects.filter(review=review), 2)

    def decisionSupervisorTest(self):
        start_review(self.p1)
        review = Review.objects.filter(proposal=self.p1)[0]
        self.assertEqual(review.go, None)

        decision = Decision.objects.filter(review=review)[0]
        decision.go = True
        decision.save()

        self.assertEqual(review.go, True)

    def decisionCommissionTest(self):
        start_review(self.p2)
        review = Review.objects.filter(proposal=self.p2)[0]
        self.assertEqual(review.go, None)

        decisions = Decision.objects.filter(review=review)
        self.assertEqual(decisions, 2)

        decisions[0].go = True
        decisions[0].save()

        self.assertEqual(review.go, None)  # undecided

        decisions[1].go = False
        decisions[1].save()

        self.assertEqual(review.go, False)  # no go

        decisions[1].go = True
        decisions[1].save()

        self.assertEqual(review.go, True)  # go
