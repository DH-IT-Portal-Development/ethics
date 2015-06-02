from datetime import datetime

from django.test import TestCase
from django.contrib.auth.models import User

from .models import Proposal, Relation
from .utils import generate_ref_number


class ProposalTestCase(TestCase):
    fixtures = ['relations']

    def setUp(self):
        self.user = User.objects.create_user(username='test0101', email='test@test.com', password='secret')
        self.relation = Relation.objects.get(pk=4)
        self.p1 = Proposal.objects.create(title='p1', reference_number=generate_ref_number(self.user), created_by=self.user, relation=self.relation)

    def test_reference_number(self):
        current_year = str(datetime.now().year)

        ref_number2 = generate_ref_number(self.user)
        self.assertEqual(ref_number2, 'test0101-02-' + current_year)

        p2 = Proposal.objects.create(title='p2', reference_number=ref_number2, created_by=self.user, relation=self.relation)
        ref_number3 = generate_ref_number(self.user)
        self.assertEqual(ref_number3, 'test0101-03-' + current_year)

        p2.delete()

        ref_number4 = generate_ref_number(self.user)
        self.assertEqual(ref_number4, 'test0101-02-' + current_year)

        self.p1.delete()

        ref_number5 = generate_ref_number(self.user)
        self.assertEqual(ref_number5, 'test0101-01-' + current_year)

        user2 = User.objects.create_user(username='test0102', email='test@test.com', password='secret')
        p3 = Proposal.objects.create(title='p3', reference_number=generate_ref_number(user2), created_by=user2, relation=self.relation)
        self.assertEqual(p3.reference_number, 'test0102-01-' + current_year)
