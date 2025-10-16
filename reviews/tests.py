from copy import copy

from django.conf import settings
from django.core import mail
from django.contrib.auth.models import User, Group, AnonymousUser
from django.test import TestCase
from django.utils import timezone

from proposals.tests import BaseProposalTestCase
from .models import Review, Decision
from .utils import (
    start_review,
    auto_review,
    auto_review_observation,
    notify_secretary,
)
from main.tests import BaseViewTestCase
from main.models import YesNoDoubt
from proposals.models import Proposal, Relation, Wmo
from studies.models import Study, Compensation, AgeGroup, Registration
from observations.models import Observation
from reviews.utils.review_utils import remind_supervisor_reviewers
from tasks.models import Session, Task

from .views import ReviewCloseView


class BaseReviewTestCase(BaseProposalTestCase):
    relation_pk = 1
    review = None

    def setUp(self):
        super().setUp()

    def setup_proposal(self):
        # Overrides parent
        self.proposal = Proposal.objects.get(
            reference_number="25-009-01", title="Normal test proposal with supervisor"
        )
        self.proposal.generate_pdf()

        self.proposal.wmo = Wmo.objects.create(
            proposal=self.proposal,
            metc=YesNoDoubt.NO,
        )
        self.proposal.save()

        self.proposal.study = Study.objects.create(
            proposal=self.proposal,
            order=1,
            compensation=Compensation.objects.get(
                pk=2,
            ),
        )
        # self.proposal.study = Study.objects.get(pk=5)
        # self.study2 = Study.objects.get(pk=5)

        self.pre_assessment = Proposal.objects.get(
            reference_number="25-012-01",
            title="Preassessment test proposal with supervisor",
        )
        self.pre_assessment.wmo = Wmo.objects.create(
            proposal=self.pre_assessment,
            metc=YesNoDoubt.NO,
        )
        self.pre_assessment.study = Study.objects.create(
            proposal=self.pre_assessment,
            order=1,
            compensation=Compensation.objects.get(
                pk=2,
            ),
        )
        self.pre_assessment.save()

    def refresh(self):
        super().refresh()
        self.review.refresh_from_db()

    def check_subject_lines(self, outbox):
        """
        Make sure every outgoing email contains a reference number and the
        text FETC-GW
        """
        for message in outbox:
            subject = message.subject
            self.assertTrue("FETC-GW" in subject)
            self.assertTrue(self.proposal.reference_number in subject)

    def remove_supervisor_from_proposal(self):
        self.proposal.relation = Relation.objects.get(
            description_nl="als postdoc, UD, UHD, of HL"
        )
        self.proposal.supervisor = None
        self.proposal.save()


class InterferenceTestCase(BaseReviewTestCase):
    """Checks if tests interact with each other. More specifically, if the fixtures remain correct,
    most likely temp tests to prove they don't"""

    def test_create_interference(self):
        self.proposal.title = "This title is changed between tests"
        self.proposal.save()
        self.changed_proposal = Proposal.objects.get(pk=4)
        self.assertEqual(
            self.changed_proposal.title, "This title is changed between tests"
        )

    def test_interference(self):
        self.changed_proposal = Proposal.objects.get(pk=4)
        self.assertNotEqual(
            self.changed_proposal.title,
            "This title is changed between tests",
            "If this test goes wrong then that means the DB has changed between tests. Something that should not happen.",
        )


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
        self.check_subject_lines(mail.outbox)
        mail.outbox = []

    def test_start_review(self):
        # If the Relation on a Proposal does not require a supervisor, a assignment review should be started.
        self.remove_supervisor_from_proposal()

        review = start_review(self.proposal)
        self.assertEqual(review.stage, Review.Stages.ASSIGNMENT)
        self.assertEqual(review.is_committee_review, True)
        self.assertEqual(Decision.objects.filter(reviewer=self.secretary).count(), 1)
        self.assertEqual(Decision.objects.filter(review=review).count(), 1)
        self.assertEqual(review.decision_set.count(), 1)

        self.assertEqual(len(mail.outbox), 2)
        self.check_subject_lines(mail.outbox)


class PreAssessmentReviewTestCase(ReviewTestCase):

    def setUp(self):
        super().setUp()
        self.proposal = self.pre_assessment


class SupervisorTestCase(BaseReviewTestCase):

    def test_supervisor_review(self):
        """
        Tests the creation of supervisor reviews
        """
        review = start_review(self.proposal)
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
        self.check_subject_lines(mail.outbox)
        # Clear outbox
        mail.outbox = []

        # Create a negative decision
        decision = Decision.objects.get(review=review)
        decision.go = Decision.Approval.NEEDS_REVISION
        decision.save()
        # Check notifications
        expected_emails = self.proposal.applicants.count()
        self.assertEquals(len(mail.outbox), expected_emails)
        remind_supervisor_reviewers()
        # No more reminders after decision is made
        self.assertEquals(len(mail.outbox), expected_emails)

    def test_negative_supervisor_decision(self):
        review = start_review(self.proposal)
        self.assertEqual(review.go, None)

        # Create a negative decision
        decision = Decision.objects.get(review=review)
        decision.go = Decision.Approval.NEEDS_REVISION
        decision.save()
        review.refresh_from_db()
        self.assertEqual(review.go, False)

    def test_positive_supervisor_decision(self):
        review = start_review(self.proposal)
        self.assertEqual(review.go, None)

        # Create a negative decision
        decision = Decision.objects.get(review=review)
        decision.go = Decision.Approval.APPROVED
        decision.save()
        review.refresh_from_db()
        self.assertEqual(review.go, True)

        review = self.proposal.latest_review()
        self.assertEqual(review.stage, review.Stages.ASSIGNMENT)


class PreAssessmentSupervisorTestCase(SupervisorTestCase):

    def setUp(self):
        super().setUp()
        self.proposal = self.pre_assessment


class CommissionTestCase(BaseReviewTestCase):
    def test_decision_commission(self):
        """
        Tests whether the commission phase in a Review works correctly.
        """
        self.remove_supervisor_from_proposal()
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


class PreAssessmentCommissionTestCase(CommissionTestCase):

    def setUp(self):
        super().setUp()
        self.proposal = self.pre_assessment


class AutoReviewTests(BaseReviewTestCase):

    def setUp(self):
        super().setUp()
        self.studyShortCut()

    def studyShortCut(self):
        self.study = self.proposal.study

    def test_auto_review(self):
        reasons = auto_review(self.proposal)
        self.assertEqual(len(reasons), 0)

        self.study.legally_incapable = True
        self.study.save()

        reasons = auto_review(self.proposal)

        self.assertEqual(len(reasons), 1)
        self.assertEqual(
            reasons[-1], "De aanvraag bevat het gebruik van wilsonbekwame volwassenen."
        )

        self.study.deception = YesNoDoubt.DOUBT
        self.study.save()

        reasons = auto_review(self.proposal)
        self.assertEqual(len(reasons), 2)
        self.assertEqual(reasons[-1], "De aanvraag bevat het gebruik van misleiding.")

        self.study.hierarchy = True
        self.study.save()

        reasons = auto_review(self.proposal)
        self.assertEqual(len(reasons), 3)
        self.assertEqual(
            reasons[-1],
            "Er bestaat een hiërarchische relatie tussen de onderzoeker(s) en deelnemer(s)",
        )

        self.study.has_special_details = True
        self.study.save()

        reasons = auto_review(self.proposal)
        self.assertEqual(len(reasons), 4)
        self.assertEqual(
            reasons[-1],
            "Het onderzoek verzamelt bijzondere persoonsgegevens.",
        )

        self.study.has_traits = True
        self.study.save()

        reasons = auto_review(self.proposal)
        self.assertEqual(len(reasons), 5)
        self.assertEqual(
            reasons[-1],
            "Het onderzoek selecteert deelnemers op bijzondere kenmerken die wellicht verhoogde kwetsbaarheid met zich meebrengen.",
        )

        self.study.risk = YesNoDoubt.YES
        self.study.save()

        reasons = auto_review(self.proposal)
        self.assertEqual(len(reasons), 6)
        self.assertEqual(
            reasons[-1],
            "De onderzoeker geeft aan dat er mogelijk kwesties zijn rondom de veiligheid van de deelnemers tijdens of na het onderzoek.",
        )

        self.study.proposal.researcher_risk = YesNoDoubt.YES
        self.study.proposal.save()

        reasons = auto_review(self.proposal)
        self.assertEqual(len(reasons), 7)
        self.assertEqual(
            reasons[-1],
            "De onderzoeker geeft aan dat er mogelijk kwesties zijn rondom de veiligheid van de betrokken onderzoekers.",
        )

        self.study.negativity = YesNoDoubt.YES
        self.study.save()

        reasons = auto_review(self.proposal)
        self.assertEqual(len(reasons), 8)

    def test_auto_review_minors_to_longroute(self):
        self.study.age_groups.set([AgeGroup.objects.get(description_nl="Peuter")])
        self.study.save()

        reasons = auto_review(self.proposal)
        self.assertEqual(len(reasons), 1)

    def test_auto_review_adults_to_shortroute(self):
        self.study.age_groups.set([AgeGroup.objects.get(description_nl="Volwassene")])
        self.study.save()

        reasons = auto_review(self.proposal)
        self.assertEqual(len(reasons), 0)

    def test_auto_review_session_time(self):
        self.study.has_sessions = True
        self.study.age_groups.set([AgeGroup.objects.get(description_nl="Peuter")])
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
        self.study.has_sessions = True
        self.study.age_groups.set([AgeGroup.objects.get(description_nl="Adolescent")])
        self.study.save()

        reasons = auto_review(self.proposal)
        self.assertEqual(len(reasons), 1)  # adolescents are minors

        self.study.registrations.set(
            [
                Registration.objects.get(
                    description="psychofysiologische meting (bijv. EEG, fMRI, EMA)"
                )
            ]
        )

        reasons = auto_review(
            self.proposal,
        )
        # reason: psychofysiological_measurements for minors detected
        self.assertEqual(len(reasons), 2)


class PreAssessmentAutoReviewTestCase(AutoReviewTests):

    def setUp(self):
        super().setUp()
        self.proposal = self.pre_assessment

    def studyShortCut(self):
        self.study = self.pre_assessment.study


class ReviewCloseTestCase(
    BaseViewTestCase,
    BaseReviewTestCase,
):
    view_class = ReviewCloseView

    def setUp(self):
        super().setUp()
        self.startReview()

    def startReview(self):
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
            f"'{self.review.get_stage_display()}' does not match",
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


class PreAssessmentReviewCloseTestCase(ReviewCloseTestCase):

    def setUp(self):
        super().setUp()
        self.proposal = self.pre_assessment

    def startReview(self):
        # super().startReview()
        self.review = start_review(self.pre_assessment)

    def test_long_route(self):
        pass
