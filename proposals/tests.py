from datetime import datetime

from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User, Group
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings

from main.models import Setting, YesNoDoubt.YES, NO
from interventions.models import Intervention
from observations.models import Observation
from tasks.models import Session, Task, Registration
from studies.models import Study, Recruitment
from .api.views import MyProposalsApiView
from .copy import copy_proposal
from .models import Proposal, Relation, Wmo, Institution
from .utils import generate_ref_number, check_local_facilities, generate_revision_ref_number


class BaseProposalTestCase(TestCase):
    fixtures = ['relations', 'compensations', 'recruitments', 'settings',
                'registrations', 'groups', 'institutions']

    def setUp(self):
        self.user = User.objects.create_user(username='test0101', email='test@test.com', password='secret')
        self.secretary = User.objects.create_user(
            username='secretarytest010101',
            email='test@test.nl',
            password='more_secret')
        Group.objects.get(name=settings.GROUP_PRIMARY_SECRETARY).user_set.add(self.secretary)
        self.chamber = Group.objects.get(name=settings.GROUP_LINGUISTICS_CHAMBER)
        self.institution = Institution.objects.get(pk=1)
        self.chamber.user_set.add(self.secretary)
        self.relation = Relation.objects.get(pk=4)
        self.p1 = Proposal.objects.create(title='p1', reference_number=generate_ref_number(),
                                          date_start=datetime.now(),
                                          created_by=self.user,
                                          relation=self.relation,
                                          reviewing_committee=self.chamber,
                                          institution=self.institution)
        self.p1.applicants.add(self.user)
        self.p1.save()


class ProposalTestCase(BaseProposalTestCase):
    def test_reference_number(self):
        current_year = str(datetime.now().year)

        # Add a proposal for the same user, check new reference number
        ref_number = generate_ref_number()
        p2 = Proposal.objects.create(title='p2', reference_number=ref_number,
                                     date_start=datetime.now(),
                                     created_by=self.user,
                                     relation=self.relation,
                                     reviewing_committee=self.chamber,
                                     institution=self.institution)
        self.assertEqual(ref_number, current_year[2:] + '-002-01')

        # Delete a proposal, check new reference number
        p2.delete()
        ref_number2 = generate_ref_number()
        Proposal.objects.create(title='p2', reference_number=ref_number2,
                                date_start=datetime.now(),
                                created_by=self.user,
                                relation=self.relation,
                                reviewing_committee=self.chamber,
                                institution=self.institution)
        self.assertEqual(ref_number2, current_year[2:] + '-002-01')

        # Add a proposal for another user
        user2 = User.objects.create_user(username='test0102', email='test@test.com', password='secret')
        p3 = Proposal.objects.create(title='p3', reference_number=generate_ref_number(),
                                     date_start=datetime.now(),
                                     created_by=user2,
                                     relation=self.relation,
                                     reviewing_committee=self.chamber,
                                     institution=self.institution)
        self.assertEqual(p3.reference_number, current_year[2:] + '-003-01')

    def test_revision_reference_number(self):
        current_year = str(datetime.now().year)

        # Add a revision proposal for p1, check new reference number
        # Should be 01-02 (first proposal, second version)
        ref_number = generate_revision_ref_number(self.p1)
        p2 = Proposal.objects.create(title='p2', reference_number=ref_number,
                                     date_start=datetime.now(),
                                     created_by=self.user,
                                     relation=self.relation,
                                     reviewing_committee=self.chamber,
                                     is_revision=True,
                                     parent=self.p1,
                                     institution=self.institution)
        self.assertEqual(ref_number, current_year[2:] + '-001-02')

        # Add a proposal for the same user, check new reference number
        # Should be 02-01 (second proposal, first version)
        ref_number = generate_ref_number()
        p3 = Proposal.objects.create(title='p3', reference_number=ref_number,
                                     date_start=datetime.now(),
                                     created_by=self.user,
                                     relation=self.relation,
                                     reviewing_committee=self.chamber,
                                     institution=self.institution)
        self.assertEqual(ref_number, current_year[2:] + '-002-01')

        # Add new proposal using an old 3-part ref.number and make a revision
        # number using the proposal.
        # Should be 97-001-02 (First proposal in 1997, second version)
        # (The year in the ref.num. and the creation_date won't line up,
        # but in this case it doesn't matter as generate_revision_ref_number
        # only looks at the ref.num. of the parent).
        p4 = Proposal.objects.create(title='p4',
                                     reference_number='97-001-01',
                                     date_start=datetime.now(),
                                     created_by=self.user,
                                     relation=self.relation,
                                     reviewing_committee=self.chamber,
                                     institution=self.institution)
        ref_number = generate_revision_ref_number(p4)
        p2 = Proposal.objects.create(title='p5', reference_number=ref_number,
                                     date_start=datetime.now(),
                                     created_by=self.user,
                                     relation=self.relation,
                                     reviewing_committee=self.chamber,
                                     is_revision=True,
                                     parent=p4,
                                     institution=self.institution)
        self.assertEqual(ref_number, '97-001-02')

        # Generate a new revision ref.number using the original proposal
        # This tests whether the right version number is created even if the
        # parent isn't the latest version
        # Should be 01-03-1997 (First proposal in 1997, third version)
        ref_number = generate_revision_ref_number(p4)
        self.assertEqual(ref_number, '97-001-03')


    def test_status(self):
        proposal = self.p1
        self.assertEqual(proposal.status, Proposal.DRAFT)

        wmo = Wmo.objects.create(proposal=proposal, metc=YesNoDoubt.YES)
        self.assertEqual(proposal.wmo.status, Wmo.WAITING)
        wmo.metc = NO
        wmo.save()
        self.assertEqual(proposal.wmo.status, Wmo.NO_WMO)
        #self.assertEqual(proposal.continue_url(), '/studies/create/1/')

        s = Study.objects.create(proposal=proposal, order=1)
        #self.assertEqual(proposal.continue_url(), '/studies/design/1/')

        s.sessions_number = 2
        s.save()
        s1 = Session.objects.create(study=s, order=1)
        s2 = Session.objects.create(study=s, order=2)

        s1.tasks_number = 2
        s1.save()

        s1_t1 = Task.objects.create(session=s1, order=1, name='t1')
        Task.objects.create(session=s1, order=2, name='t2')

        s1.tasks_duration = 45
        s1.save()
        self.assertEqual(proposal.current_session(), s2)

        s1_t1.delete()
        self.assertEqual(proposal.current_session(), s1)

    def test_check_local_facilities(self):
        # By default there are no local facilities in use
        self.assertEqual(len(check_local_facilities(self.p1)), 0)

        # If we create a Study and add local Recruitment, facilities should be returned
        s = Study.objects.create(proposal=self.p1, order=1)
        s.save()

        recruitments = Recruitment.objects.filter(is_local=True)
        s.recruitment.set(recruitments)
        s.save()

        facs = check_local_facilities(self.p1)
        self.assertEqual(len(facs), 1)
        self.assertSetEqual(facs[Recruitment._meta.verbose_name], set([r.description for r in recruitments]))

        # If we remove local Recruitment, we should again return no facilities
        s.recruitment.set(Recruitment.objects.filter(is_local=False))
        s.save()
        self.assertEqual(len(check_local_facilities(self.p1)), 0)

        # If we add an Invervention part, we should return facilities when we add local Settings
        s.has_intervention = True
        s.save()
        i = Intervention.objects.create(study=s, amount_per_week=1, duration=1)
        self.assertEqual(len(check_local_facilities(self.p1)), 0)

        settings = Setting.objects.filter(is_local=True)
        i.setting.set(settings)
        i.save()

        facs = check_local_facilities(self.p1)
        self.assertEqual(len(facs), 1)
        self.assertSetEqual(facs[Setting._meta.verbose_name], set([st.description for st in settings]))

        # If we add a Sessions part, we should return facilities when we add local Registrations
        s.has_sessions = True
        s.sessions_number = 2
        s.save()
        s1 = Session.objects.create(study=s, order=1)

        s1.tasks_number = 2
        s1.save()

        s1_t1 = Task.objects.create(session=s1, order=1, name='t1')

        registrations = Registration.objects.filter(is_local=True)
        s1_t1.registrations.set(registrations)
        s1_t1.save()

        facs = check_local_facilities(self.p1)
        self.assertEqual(len(facs), 2)
        self.assertSetEqual(facs[Registration._meta.verbose_name], set([r.description for r in registrations]))


class ProposalsViewTestCase(BaseProposalTestCase):
    def setUp(self):
        super(ProposalsViewTestCase, self).setUp()
        self.factory = RequestFactory()

    def test_supervisor(self):
        request = self.factory.get('/proposals/api/my_archive')
        request.user = self.user

        response = MyProposalsApiView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['items'][0]['pk'], self.p1.pk)

        # Add a Proposal for another User
        user2 = User.objects.create_user(username='test0102', email='test@test.com', password='secret')
        p2 = Proposal.objects.create(title='p3', reference_number=generate_ref_number(),
                                     date_start=datetime.now(),
                                     created_by=user2,
                                     relation=self.relation,
                                     reviewing_committee=self.chamber,
                                     institution=self.institution)
        p2.applicants.add(user2)
        p2.save()

        # Sanity test: response should still be the same
        response = MyProposalsApiView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['items'][0]['pk'], self.p1.pk)

        # Second user should only see his Proposal
        request.user = user2
        response = MyProposalsApiView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['items'][0]['pk'], p2.pk)

        # If we set self.user to be the supervisor, he should see both Proposals
        p2.supervisor = self.user
        p2.save()

        request.user = self.user
        response = MyProposalsApiView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertSequenceEqual(
            [
                response.data['items'][0]['pk'],
                response.data['items'][1]['pk']
            ],
            [self.p1.pk, p2.pk]
        )


class WmoTestCase(BaseProposalTestCase):
    def setUp(self):
        super(WmoTestCase, self).setUp()
        self.wmo = Wmo.objects.create(proposal=self.p1, metc=NO)

    def test_status(self):
        self.assertEqual(self.wmo.status, Wmo.NO_WMO)

        self.wmo.metc = YesNoDoubt.YES
        self.wmo.save()

        self.assertEqual(self.wmo.status, Wmo.WAITING)

        self.wmo.metc_decision = True
        self.wmo.save()

        self.assertEqual(self.wmo.status, Wmo.WAITING)

        self.wmo.metc_decision_pdf = SimpleUploadedFile('test.pdf', b'contents')
        self.wmo.save()

        self.assertEqual(self.wmo.status, Wmo.JUDGED)


class CopyTestCase(BaseProposalTestCase):

    def setUp(self):
        super().setUp()

        self.wmo_1 = Wmo.objects.create(
            proposal=self.p1,
            metc=Wmo.JUDGED,
        )

        self.study_1 = Study.objects.create(
            proposal=self.p1,
            order=1,
            name="Study 1",
            has_intervention=True,
            has_sessions=True,
            has_observation=True,
        )
        self.intervention_1 = Intervention.objects.create(
            study=self.study_1,
            description="Intervention 1",
        )
        self.observation_1 = Observation.objects.create(
            study=self.study_1,
            details_who="Observation 1",
        )
        self.session_1 = Session.objects.create(
            study=self.study_1,
            order=1,
            tasks_number=1,
        )
        self.task_1 = Task.objects.create(
            session=self.session_1,
            name="Task 1",
            order=1,
        )

    def test_parent_present_for_rev(self):
        """Test if parent is set when making a revision/amendment copy"""
        p2 = copy_proposal(
            self.p1,
            True,
            self.user
        )

        self.assertIsNotNone(p2.parent)
        self.assertEqual(p2.parent.pk, self.p1.pk)

    def test_parent_missing_for_copy(self):
        """Test if parent is missing if making a regular copy"""
        p2 = copy_proposal(
            self.p1,
            False,
            self.user
        )

        self.assertIsNone(p2.parent)

    def test_related_copying(self):
        """Test if related objects are copied during copying"""
        p2 = copy_proposal(
            self.p1,
            False,
            self.user
        )

        self.assertEqual(p2.study_set.count(), 1)

        study = p2.study_set.first()

        self.assertIsNotNone(study.observation)
        self.assertEqual(study.observation.details_who, "Observation 1")

        self.assertIsNotNone(study.intervention)
        self.assertEqual(study.intervention.description, "Intervention 1")

        self.assertEqual(study.session_set.count(), 1)

        session = study.session_set.first()
        self.assertEqual(session.task_set.count(), 1)
        task = session.task_set.first()
        self.assertEqual(task.name, "Task 1")
