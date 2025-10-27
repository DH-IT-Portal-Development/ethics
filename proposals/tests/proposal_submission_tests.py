import logging

from django.contrib.auth.models import User, Group, AnonymousUser
from django.conf import settings
from django.test import TestCase

from main.tests import BaseViewTestCase
from proposals.models import Proposal, Relation, Wmo
from reviews.models import Review

from proposals.views.proposal_views import (
    ProposalSubmit,
    ProposalSubmitPreApproved,
    ProposalSubmitPreAssessment,
)
from studies.models import Study


class BaseProposalTestCase(TestCase):
    fixtures = [
        "groups",
        "settings",
        "fundings",
        "institutions",
        "relations",
        "studentcontexts",
        "agegroups",
        "compensations",
        "recruitments",
        "specialdetails",
        "traits",
        "00_registrations",
        "01_registrationkinds",
        "testing/test_users",
        "testing/test_proposals",
        "testing/test_wmos",
    ]

    def setUp(self):
        self.setup_users()
        self.setup_proposal()

        # Disable logging warnings and all levels below
        # Our (pdf) code logs warnings that are not relevant to the tests
        # ERROR and CRITICAL are still logged
        logging.disable(logging.WARN)

    def setup_users(self):
        self.secretary = User.objects.get(username="secretary")
        self.c1 = User.objects.get(username="c1")
        self.c2 = User.objects.get(username="c2")
        self.user = User.objects.get(username="user")
        self.supervisor = User.objects.get(username="supervisor")

    def setup_proposal(self):
        """
        Load our test proposals from a fixture.
        """
        self.proposal = Proposal.objects.get(pk=1)
        self.pre_assessment = Proposal.objects.get(pk=2)
        self.pre_approval = Proposal.objects.get(pk=3)

    def refresh(self):
        """Refresh objects from DB. This is sometimes necessary if you access
        attributes you previously read during the test and don't want to
        receive a cached value."""
        self.proposal.refresh_from_db()


class ProposalSubmitTestCase(
    BaseViewTestCase,
    BaseProposalTestCase,
):
    view_class = ProposalSubmit

    def get_view_path(self):
        pk = self.proposal.pk
        return f"/proposals/submit/{pk}/"

    def get_view_args(self):
        return {"pk": self.proposal.pk}

    def get_post_data(self):
        return {
            "inform_local_staff": True,
            "embargo": True,
            "comments": "asdf",
            "embargo_end_date": "2025-01-01",
        }

    def test_access(
        self,
    ):
        # NB: The proposal creator does not have access by default
        # Be sure to add them to the applicants list as well.
        self.assertEqual(
            self.check_access(
                self.proposal.created_by,
            ),
            True,
        )
        self.assertEqual(
            self.check_access(
                AnonymousUser,
            ),
            False,
        )

    def test_submission_unsupervised(self):
        """
        Tests the following:
        - The current proposal is a draft
        - An applicant can submit a proposal that has no errors
        - Because there is no supervisor, a new review is created
          in the assignment stage.
        """
        # Sanity checks to start
        self.assertEqual(
            self.proposal.status,
            self.proposal.Statuses.DRAFT,
        )
        self.assertEqual(
            self.proposal.latest_review(),
            None,
        )
        # POST and check status code
        self.client.force_login(self.user)
        page = self.post(
            self.get_post_data(),
            user=self.user,
        )

        self.assertIn(page.status_code, [302, 200])
        self.refresh()
        # Post-submission tests
        self.assertNotEqual(
            # if you fail this test then it's a possibility that you have added a new field
            # ,and you have yet to add proposal test data
            self.proposal.status,
            self.proposal.Statuses.DRAFT,
        )
        self.assertNotEqual(
            self.proposal.latest_review(),
            None,
        )
        self.assertEqual(
            self.proposal.latest_review().stage,
            Review.Stages.ASSIGNMENT,
        )

    def test_proposal_supervised(self):
        """
        Tests the following:
        - The current proposal is a draft
        - An applicant can submit a proposal that has no errors
        - Because there is a supervisor, a new review is created
          in the supervisor stage.
        """
        # Select the PHD relation, which needs a supervisor
        # but doesn't check for a study/course
        self.proposal.relation = Relation.objects.get(pk=4)
        self.proposal.supervisor = self.supervisor
        self.proposal.save()
        # Sanity checks to start
        self.assertEqual(
            self.proposal.status,
            self.proposal.Statuses.DRAFT,
        )
        self.assertEqual(
            self.proposal.latest_review(),
            None,
        )
        # POST and check status code
        self.client.force_login(self.user)
        page = self.post(
            self.get_post_data(),
            user=self.user,
        )
        self.assertIn(page.status_code, [302, 200])
        self.refresh()
        # Post-submission tests
        self.assertNotEqual(
            self.proposal.status,
            self.proposal.Statuses.DRAFT,
        )
        self.assertNotEqual(
            self.proposal.latest_review(),
            None,
        )
        self.assertEqual(
            self.proposal.latest_review().stage,
            Review.Stages.SUPERVISOR,
        )


class PreassessmentSubmitTestCase(
    ProposalSubmitTestCase,
):
    view_class = ProposalSubmitPreAssessment

    def setUp(self):
        super().setUp()
        self.proposal = self.pre_assessment
        wmo = Wmo(
            status=0,
            metc="N",
            is_medical="N",
        )
        wmo.save()
        self.proposal.wmo = wmo


class PreapprovedSubmitTestCase(
    ProposalSubmitTestCase,
):
    view_class = ProposalSubmitPreApproved

    def setUp(self):
        super().setUp()
        self.proposal = self.pre_approval
