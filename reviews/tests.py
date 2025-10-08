from datetime import date, timedelta
from copy import copy

from django.conf import settings
from django.core import mail
from django.contrib.auth.models import User, Group, AnonymousUser
from django.test import TestCase
from django.utils import timezone

from .models import Review, Decision
from .utils import (
    start_review,
    auto_review,
    auto_review_observation,
    notify_secretary,
)
from main.tests import BaseViewTestCase
from main.models import YesNoDoubt
from proposals.models import Proposal, Relation, Wmo, Funding
from proposals.utils import generate_ref_number
from studies.models import Study, Compensation, AgeGroup, Registration
from observations.models import Observation
from reviews.utils.review_utils import remind_supervisor_reviewers
from interventions.models import Intervention
from tasks.models import Session, Task

from .views import ReviewCloseView


class BaseReviewTestCase(TestCase):
    fixtures = [
        "relations",
        "compensations",
        "00_registrations",
        "01_registrationkinds",
        "agegroups",
        "groups",
        "institutions",
        "fundings",
    ]
    relation_pk = 1

    def setUp(self):
        """
        Sets up the Users and a default Proposal to use in the tests below.
        """
        self.setup_users()
        self.setup_proposal()
        super().setUp()

    def setup_proposal(self):
        self.proposal = Proposal.objects.create(
            title="p1",
            reference_number=generate_ref_number(),
            date_start=date.today(),
            created_by=self.user,
            supervisor=self.supervisor,
            relation=Relation.objects.get(pk=4),
            reviewing_committee=Group.objects.get(
                name=settings.GROUP_LINGUISTICS_CHAMBER
            ),
            institution_id=1,
        )
        self.proposal.applicants.add(
            self.user,
        )
        self.proposal.wmo = Wmo.objects.create(
            proposal=self.proposal,
            metc=YesNoDoubt.NO,
        )
        self.study = Study.objects.create(
            proposal=self.proposal,
            order=1,
            compensation=Compensation.objects.get(
                pk=2,
            ),
        )
        self.proposal.generate_pdf()

    def setup_users(self):
        self.secretary = User.objects.create_user(
            "secretary",
            "test@test.com",
            "secret",
            first_name="The",
            last_name="Secretary",
        )
        self.c1 = User.objects.create_user("c1", "test@test.com", "secret")
        self.c2 = User.objects.create_user("c2", "test@test.com", "secret")
        self.user = User.objects.create_user(
            "user", "test@test.com", "secret", first_name="John", last_name="Doe"
        )
        self.supervisor = User.objects.create_user(
            "supervisor", "test@test.com", "secret", first_name="Jane", last_name="Roe"
        )

        self.secretary.groups.add(
            Group.objects.get(name=settings.GROUP_PRIMARY_SECRETARY)
        )
        self.secretary.groups.add(Group.objects.get(name=settings.GROUP_SECRETARY))
        self.c1.groups.add(Group.objects.get(name=settings.GROUP_LINGUISTICS_CHAMBER))
        self.c2.groups.add(Group.objects.get(name=settings.GROUP_LINGUISTICS_CHAMBER))

    def refresh(self):
        """Refresh objects from DB. This is sometimes necessary if you access
        attributes you previously read during the test and don't want to
        receive a cached value."""
        self.review.refresh_from_db()
        self.proposal.refresh_from_db()

    def check_subject_lines(self, proposal: Proposal, outbox):
        """
        Make sure every outgoing email contains a reference number and the
        text FETC-GW
        """
        for message in outbox:
            subject = message.subject
            self.assertTrue("FETC-GW" in subject)
            self.assertTrue(proposal.reference_number in subject)


class BasePreAssessmentTestCase(BaseReviewTestCase):
    def setUp(self):
        super().setUp()
        self.student: Relation = Relation.objects.get(pk=4)
        self.language_sciences_pk = 1
        self.direct_funding: Funding = Funding.objects.get(pk=2)
        self.setup_pre_assessment()

    def setup_pre_assessment(self):
        """Create pre-assessment data. also called Preliminary assessment."""
        self.pre_assessment = Proposal.objects.create(
            is_pre_assessment=True,
            created_by=self.user,
            reference_number=generate_ref_number(),
            # 1. basic details
            # What is the title of your application? This title will be used in all formal correspondence.
            title="pre_proposal",
            # What is the desired starting date of the actual research for which this application is being submitted?
            date_start=date.today(),
            # What is the expected end date of the research for which this application is being submitted?
            expected_end_date=date.today() + timedelta(days=1),
            # To which research institute are you affiliated?
            institution_id=self.language_sciences_pk,
            reviewing_committee=Group.objects.get(
                name=settings.GROUP_LINGUISTICS_CHAMBER
            ),
            # In what capacity are you involved in this application?
            relation=self.student,
            # Promotor/Supervisor
            supervisor=self.supervisor,  # requirement: relation needs a supervisor
        )
        # Are there any other researchers involved affiliated with ICON, OFR, OGK or ILS?
        self.pre_assessment.applicants.add(
            self.user,
        )
        # Are there any other researchers involved outside the above-mentioned institutes?
        self.pre_assessment.other_stakeholders = False
        # How is this study funded?
        self.pre_assessment.funding.add(self.direct_funding)
        # Upload your application here (in .pdf or .doc(x)-format)
        self.pre_assessment.pre_assessment_pdf = None
        # What are the most important ethical considerations in this research?
        self.pre_assessment.self_assessment = "Wat zijn de belangrijkste ethische kwesties in dit onderzoek en beschrijf kort hoe je daarmee omgaat."
        # 2. WMO
        # Will the data collection take place at the UMC Utrecht or another institution for which an assessment by a METC is required?
        # Is the nature of the research question medical (as defined by the Medical Research Involving Human Subjects Act (WMO))?
        self.pre_assessment.wmo = Wmo.objects.create(
            proposal=self.pre_assessment,
            metc=YesNoDoubt.NO,
        )
        # 3. Documents
        # Optional File
        # No Data yet added
        # 4. Submit
        # Space for possible comments. Use a maximum of 1000 words.
        self.pre_assessment.comments = "Space for possible comments"
        self.pre_assessment.generate_pdf()  # this also generates with start_review, possible redundancy

    def refresh(self):
        super().refresh()
        self.pre_assessment.refresh_from_db()


class ReviewTestCase(BaseReviewTestCase):
    def test_start_supervisor_review(self):
        """
        Tests starting of a Review from a submitted Proposal.
        """
        # If the Relation on a Proposal requires a supervisor, a Review for the supervisor should be started.
        review = start_review(self.proposal)
        self.assertEqual(review.stage, Review.Stages.SUPERVISOR)
        self.assertEqual(review.is_committee_review, False)
        self.assertEqual(Decision.objects.filter(reviewer=self.supervisor).count(), 1)
        self.assertEqual(Decision.objects.filter(review=review).count(), 1)
        self.assertEqual(review.decision_set.count(), 1)

        self.assertEqual(len(mail.outbox), 2)  # check we sent 2 emails
        self.check_subject_lines(self.proposal, mail.outbox)
        mail.outbox = []

    def test_start_review(self):
        # If the Relation on a Proposal does not require a supervisor, a assignment review should be started.
        self.proposal.relation = Relation.objects.get(pk=5)
        self.proposal.save()

        review = start_review(self.proposal)
        self.assertEqual(review.stage, Review.Stages.ASSIGNMENT)
        self.assertEqual(review.is_committee_review, True)
        self.assertEqual(Decision.objects.filter(reviewer=self.secretary).count(), 1)
        self.assertEqual(Decision.objects.filter(review=review).count(), 1)
        self.assertEqual(review.decision_set.count(), 1)

        self.assertEqual(len(mail.outbox), 2)
        self.check_subject_lines(self.proposal, mail.outbox)


class SupervisorTestCase(BasePreAssessmentTestCase):
    def test_supervisor_review_proposal(self):
        self._test_supervisor_review(self.proposal)

    def test_supervisor_review_pre_assessment(self):
        self._test_supervisor_review(self.pre_assessment)

    def _test_supervisor_review(self, proposal: Proposal):
        """
        Tests the creation of supervisor reviews
        """
        review = start_review(proposal)
        remind_supervisor_reviewers()

        # Check for supervisor and submitter notifications
        # No reminders should have been sent yet
        self.assertEqual(len(mail.outbox), 2)
        today = timezone.now().date()
        yesterday = today - timezone.timedelta(days=1)
        review.date_should_end = yesterday
        review.save()

        # Reminders should now be sent
        remind_supervisor_reviewers()
        self.assertEqual(len(mail.outbox), 3)
        self.check_subject_lines(proposal, mail.outbox)
        # Clear outbox
        mail.outbox = []

        # Create a negative decision
        decision = Decision.objects.get(review=review)
        decision.go = Decision.Approval.NEEDS_REVISION
        decision.save()
        # Check notifications
        expected_emails = proposal.applicants.count()
        self.assertEquals(len(mail.outbox), expected_emails)
        remind_supervisor_reviewers()
        # No more reminders after decision is made
        self.assertEquals(len(mail.outbox), expected_emails)

    def test_negative_supervisor_decision_pre_assessment(self):
        self._test_negative_supervisor_decision(self.pre_assessment)

    def test_negative_supervisor_decision_proposal(self):
        self._test_negative_supervisor_decision(self.proposal)

    def _test_negative_supervisor_decision(self, proposal: Proposal):
        review = start_review(proposal)
        self.assertEqual(review.go, None)

        # Create a negative decision
        decision = Decision.objects.get(review=review)
        decision.go = Decision.Approval.NEEDS_REVISION
        decision.save()
        review.refresh_from_db()
        self.assertEqual(review.go, False)

    def test_positive_supervisor_decision_pre_assessment(self):
        self._test_positive_supervisor_decision(self.pre_assessment)

    def test_positive_supervisor_decision_proposal(self):
        self._test_positive_supervisor_decision(self.proposal)

    def _test_positive_supervisor_decision(self, proposal: Proposal):
        review = start_review(proposal)
        self.assertEqual(review.go, None)

        # Create a negative decision
        decision = Decision.objects.get(review=review)
        decision.go = Decision.Approval.APPROVED
        decision.save()
        review.refresh_from_db()
        self.assertEqual(review.go, True)

        review = proposal.latest_review()
        self.assertEqual(review.stage, review.Stages.ASSIGNMENT)


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
        self.assertEqual(review.stage, Review.Stages.ASSIGNMENT)
        self.assertEqual(review.go, None)

        # Create a Decision for a member of the commission group
        Decision.objects.create(review=review, reviewer=self.c1)
        review.stage = Review.Stages.COMMISSION
        review.refresh_from_db()

        self.assertEqual(len(mail.outbox), 2)

        decisions = Decision.objects.filter(review=review)
        self.assertEqual(len(decisions), 2)

        decisions[0].go = Decision.Approval.APPROVED
        decisions[0].save()
        review.refresh_from_db()
        self.assertEqual(review.go, None)  # undecided

        decisions[1].go = Decision.Approval.NOT_APPROVED
        c = 'Let\'s test "escaping" of < and >'
        decisions[1].comments = c
        decisions[1].save()
        review.refresh_from_db()
        self.assertEqual(review.go, False)  # no go

        notify_secretary(decisions[1])
        self.assertEqual(len(mail.outbox), 4)
        self.assertIn(c, mail.outbox[3].body)

        decisions[1].go = Decision.Approval.APPROVED
        decisions[1].save()
        review.refresh_from_db()
        self.assertEqual(review.go, True)  # go


class AutoReviewTests(BaseReviewTestCase):

    def setUp(self):
        super().setUp()
        self.toddlers = AgeGroup.objects.get(description_nl="Peuter")
        self.adolescents = AgeGroup.objects.get(description_nl="Adolescent")
        self.adults = AgeGroup.objects.get(description_nl="Volwassene")
        self.psychofysiological_measurement = Registration.objects.get(
            description="psychofysiologische meting (bijv. EEG, fMRI, EMA)"
        )

    def test_auto_review(self):
        reasons = auto_review(self.proposal)
        self.assertEqual(len(reasons), 0)

        self.study.legally_incapable = True
        self.study.save()

        reasons = auto_review(self.proposal)
        self.assertEqual(len(reasons), 1)

        self.study.deception = YesNoDoubt.DOUBT
        self.study.save()

        reasons = auto_review(self.proposal)
        self.assertEqual(len(reasons), 2)

        self.study.hierarchy = True
        self.study.save()

        reasons = auto_review(self.proposal)
        self.assertEqual(len(reasons), 3)

        self.study.has_special_details = True
        self.study.save()

        reasons = auto_review(self.proposal)
        self.assertEqual(len(reasons), 4)

        self.study.has_traits = True
        self.study.save()

        reasons = auto_review(self.proposal)
        self.assertEqual(len(reasons), 5)

        self.study.risk = YesNoDoubt.YES
        self.study.save()

        reasons = auto_review(self.proposal)
        self.assertEqual(len(reasons), 6)

        self.study.proposal.researcher_risk = YesNoDoubt.YES
        self.study.proposal.save()

        reasons = auto_review(self.proposal)
        self.assertEqual(len(reasons), 7)

        self.study.negativity = YesNoDoubt.YES
        self.study.save()

        reasons = auto_review(self.proposal)
        self.assertEqual(len(reasons), 8)

    def test_auto_review_minors_to_longroute(self):
        self.study.age_groups.set([self.toddlers])
        self.study.save()

        reasons = auto_review(self.proposal)
        self.assertEqual(len(reasons), 1)

    def test_auto_review_adults_to_shortroute(self):
        self.study.age_groups.set([self.adults])
        self.study.save()

        reasons = auto_review(self.proposal)
        self.assertEqual(len(reasons), 0)

    def test_auto_review_session_time(self):
        self.study.has_sessions = True
        self.study.age_groups.set([self.toddlers])
        self.study.save()

        s1 = Session.objects.create(study=self.study, order=1)
        s1_t1 = Task.objects.create(session=s1, order=1, duration=20)
        s1_t2 = Task.objects.create(session=s1, order=2, duration=20)
        self.study.save()

        self.assertEqual(s1.net_duration(), 40)
        reasons = auto_review(self.proposal)
        self.assertEqual(len(reasons), 1)  # minors go to longroute.

        s1_t2.duration = 30
        s1_t2.save()
        self.study.save()
        self.assertEqual(s1.net_duration(), 50)
        reasons = auto_review(self.proposal)
        self.assertEqual(len(reasons), 2)
        # reason: minors go to longroute, and session takes longer than 40m for the agegroup toddlers.

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

    def test_auto_review_registration_age_min(self):
        self.study.has_sessions = True  # weggehaald in develop
        self.study.age_groups.set([self.adolescents])
        self.study.save()

        reasons = auto_review(self.proposal)
        self.assertEqual(len(reasons), 1)  # adolescents are minors

        self.study.registrations.set([self.psychofysiological_measurement])

        reasons = auto_review(
            self.proposal,
        )
        # reason: psychofysiological_measurements for minors detected
        self.assertEqual(len(reasons), 2)


class ReviewCloseTestCase(
    BaseViewTestCase,
    BaseReviewTestCase,
):
    view_class = ReviewCloseView

    def setUp(self):
        super().setUp()
        self.review = start_review(self.proposal)

    def get_view_path(self):
        pk = self.review.pk
        return f"/reviews/close/{pk}/"

    def get_view_args(self):
        return {"pk": self.review.pk}

    def test_access(self):
        """Check this view is only accessible to secretary users"""
        self.assertEqual(
            self.check_access(AnonymousUser()),
            False,
        )
        self.assertEqual(
            self.check_access(self.user),
            False,
        )
        self.assertEqual(
            self.check_access(self.secretary),
            True,
        )

    def test_open_review(self):
        """Test the default state of the Review and View"""
        p = self.proposal
        self.assertEqual(
            p.status_review,
            None,
        )
        self.assertGreaterEqual(
            p.status,
            p.Statuses.SUBMITTED_TO_SUPERVISOR,
        )

    def test_decision(self):
        """
        Submit the Close form with a standard continuation
        and check the results.
        """
        previous_review_date = copy(self.proposal.date_reviewed)
        form_values = {
            # We choose GO_POST_HOC because GO (0) is already the default
            "continuation": self.review.Continuations.GO_POST_HOC,
        }
        self.client.force_login(self.secretary)
        page = self.post(
            form_values,
            user=self.secretary,
        )
        self.refresh()
        # Assertions
        self.assertNotEqual(
            self.proposal.date_reviewed,
            previous_review_date,
        )
        self.assertEqual(
            self.proposal.status,
            self.proposal.Statuses.DECISION_MADE,
        )
        self.assertEqual(
            self.proposal.status_review,
            True,
        )

    def test_long_route(self):
        # If the review uses the long route already, the form
        # won't accept this choice. So we force set it to short.
        self.review.short_route = True
        self.review.save()
        form_values = {
            "continuation": self.review.Continuations.LONG_ROUTE,
        }
        self.client.force_login(self.secretary)
        page = self.post(
            form_values,
            user=self.secretary,
        )
        self.refresh()
        # Assertions
        self.assertEqual(
            self.review.stage,
            self.review.Stages.CLOSED,
        )
        # A new review should have been created
        # with a decision
        self.assertNotEqual(
            self.review,
            Review.objects.last(),
        )
        self.assertGreater(
            Review.objects.last().decision_set.all().count(),
            0,
        )

    def test_metc(self):
        """When posted with review.METC, check that proposal is turned back
        into a Draft and its WMO gets flagged."""
        form_values = {
            "continuation": self.review.Continuations.METC,
        }
        self.client.force_login(self.secretary)
        self.post(
            form_values,
            user=self.secretary,
        )
        self.refresh()
        # Assertions
        self.assertEqual(
            self.proposal.status,
            self.proposal.Statuses.DRAFT,
        )
        self.assertEqual(
            self.proposal.wmo.enforced_by_commission,
            True,
        )
