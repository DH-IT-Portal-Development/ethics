from datetime import datetime

from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile

from .models import Proposal, Relation, Wmo, Study, Compensation, Session, Task
from .utils import generate_ref_number


class BaseProposalTestCase(TestCase):
    fixtures = ['relations', 'compensations']

    def setUp(self):
        self.user = User.objects.create_user(username='test0101', email='test@test.com', password='secret')
        self.relation = Relation.objects.get(pk=4)
        self.p1 = Proposal.objects.create(title='p1', reference_number=generate_ref_number(self.user),
                                          date_start=datetime.now(), date_end=datetime.now(),
                                          created_by=self.user, relation=self.relation)


class ProposalTestCase(BaseProposalTestCase):
    def test_reference_number(self):
        current_year = str(datetime.now().year)

        # Add a proposal for the same user, check new reference number
        ref_number = generate_ref_number(self.user)
        p2 = Proposal.objects.create(title='p2', reference_number=ref_number,
                                     date_start=datetime.now(), date_end=datetime.now(),
                                     created_by=self.user, relation=self.relation)
        self.assertEqual(ref_number, 'test0101-02-' + current_year)

        # Delete a proposal, check new reference number
        p2.delete()
        ref_number2 = generate_ref_number(self.user)
        self.assertEqual(ref_number2, 'test0101-02-' + current_year)

        # Add a proposal for another user
        user2 = User.objects.create_user(username='test0102', email='test@test.com', password='secret')
        p3 = Proposal.objects.create(title='p3', reference_number=generate_ref_number(user2),
                                     date_start=datetime.now(), date_end=datetime.now(),
                                     created_by=user2, relation=self.relation)
        self.assertEqual(p3.reference_number, 'test0102-01-' + current_year)

    def test_status(self):
        proposal = self.p1
        self.assertEqual(proposal.status, Proposal.DRAFT)

        wmo = Wmo.objects.create(proposal=proposal, metc=True)
        self.assertEqual(proposal.status, Proposal.WMO_DECISION_BY_METC)
        wmo.metc = False
        wmo.save()
        self.assertEqual(proposal.status, Proposal.WMO_DECISION_BY_ETCL)
        self.assertEqual(proposal.continue_url(), '/study/create/1/')

        compensation = Compensation.objects.get(pk=1)
        s = Study.objects.create(proposal=proposal, compensation=compensation)
        self.assertEqual(proposal.status, Proposal.STUDY_CREATED)
        self.assertEqual(proposal.continue_url(), '/session_start/1/')

        s.sessions_number = 2
        s.save()
        s1 = Session.objects.create(study=s, order=1)
        s2 = Session.objects.create(study=s, order=2)
        self.assertEqual(proposal.status, Proposal.SESSIONS_STARTED)

        s1.tasks_number = 2
        s1.save()
        self.assertEqual(proposal.status, Proposal.TASKS_STARTED)

        s1_t1 = Task.objects.create(session=s1, order=1, name='t1')
        s1_t2 = Task.objects.create(session=s1, order=2, name='t2')
        self.assertEqual(proposal.status, Proposal.TASKS_ADDED)

        s1.tasks_duration = 45
        s1.save()
        self.assertEqual(proposal.current_session(), s2)
        self.assertEqual(proposal.status, proposal.SESSIONS_STARTED)

        s1_t1.delete()
        self.assertEqual(proposal.current_session(), s1)
        self.assertEqual(proposal.status, proposal.TASKS_ADDED)


class WmoTestCase(BaseProposalTestCase):
    def setUp(self):
        super(WmoTestCase, self).setUp()
        self.wmo = Wmo.objects.create(proposal=self.p1, metc=False)

    def test_status(self):
        self.assertEqual(self.wmo.status, Wmo.NO_WMO)

        self.wmo.metc = True
        self.wmo.save()

        self.assertEqual(self.wmo.status, Wmo.WAITING)

        self.wmo.metc_decision = True
        self.wmo.save()

        self.assertEqual(self.wmo.status, Wmo.WAITING)

        self.wmo.metc_decision_pdf = SimpleUploadedFile('test.pdf', 'contents')
        self.wmo.save()

        self.assertEqual(self.wmo.status, Wmo.JUDGED)
