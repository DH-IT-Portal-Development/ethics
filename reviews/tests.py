from django.test import TestCase
from django.contrib.auth.models import User

from .models import Review, Decision
from .utils import start_review, auto_review
from proposals.models import Proposal, Study, Relation, Compensation
from proposals.utils import generate_ref_number


class ReviewTestCase(TestCase):
    fixtures = ['relations', 'compensations']

    def setUp(self):
        self.user = User.objects.create_superuser('test0101', 'test@test.com', 'secret')
        self.supervisor = User.objects.create_superuser('supervisor', 'test@test.com', 'secret')
        self.p1 = Proposal.objects.create(title='p1', reference_number=generate_ref_number(self.user),
            created_by=self.user, supervisor=self.supervisor, relation=Relation.objects.get(pk=4))
        self.p2 = Proposal.objects.create(title='p2', reference_number=generate_ref_number(self.user),
            created_by=self.user, supervisor=self.supervisor, relation=Relation.objects.get(pk=5))

    def test_start_review(self):
        review = start_review(self.p1)
        self.assertEqual(review.stage, Review.SUPERVISOR)
        self.assertEqual(Decision.objects.filter(reviewer=self.supervisor).count(), 1)
        self.assertEqual(Decision.objects.filter(review=review).count(), 1)
        self.assertEqual(review.decision_set.count(), 1)

        review = start_review(self.p2)
        self.assertEqual(review.stage, Review.COMMISSION)
        self.assertEqual(Decision.objects.filter(reviewer=self.user).count(), 1)
        self.assertEqual(Decision.objects.filter(reviewer=self.supervisor).count(), 2)
        self.assertEqual(Decision.objects.filter(review=review).count(), 2)

    def test_decision_supervisor(self):
        review = start_review(self.p1)
        self.assertEqual(review.go, None)

        decision = Decision.objects.filter(review=review)[0]
        decision.go = True
        decision.save()
        review.refresh_from_db()
        self.assertEqual(review.go, True)

    def test_decision_commission(self):
        review = start_review(self.p2)
        self.assertEqual(review.go, None)

        decisions = Decision.objects.filter(review=review)
        self.assertEqual(len(decisions), 2)

        decisions[0].go = True
        decisions[0].save()
        review.refresh_from_db()
        self.assertEqual(review.go, None)  # undecided

        decisions[1].go = False
        decisions[1].save()
        review.refresh_from_db()
        self.assertEqual(review.go, False)  # no go

        decisions[1].go = True
        decisions[1].save()
        review.refresh_from_db()
        self.assertEqual(review.go, True)  # go

    def test_auto_review(self):
        compensation = Compensation.objects.get(pk=1)
        Study.objects.create(proposal=self.p2, compensation=compensation)

        go, reasons = auto_review(self.p2)
        self.assertTrue(go)

        self.p2.study.risk_physical = True
        self.p2.study.save()

        go, reasons = auto_review(self.p2)
        self.assertFalse(go)
        self.assertEqual(len(reasons), 1)

