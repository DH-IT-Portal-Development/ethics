from django.contrib.auth.models import User, Group, AnonymousUser
from django.conf import settings
from django.test import TestCase
from django.core.management import call_command

from main.tests import BaseViewTestCase
from proposals.models import Proposal, Relation
from reviews.models import Review

from proposals.views.proposal_views import (
    ProposalSubmit,
    ProposalSubmitPreApproved,
    ProposalSubmitPreAssessment,
)


class BaseProposalTestCase(TestCase):
    fixtures = [
        "groups",
        "settings",
        "registrations",
        "fundings",
        "institutions",
        "relations",
        "studentcontexts",
        "agegroups",
        "compensations",
        "recruitments",
        "specialdetails",
        "traits",
        "registrationkinds",
        "registrations",
        "testing/test_users",
        "testing/test_proposals",
    ]

    def setUp(self):
        self.setup_users()
        self.setup_proposal()

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
            Group.objects.get(
                name=settings.GROUP_PRIMARY_SECRETARY
            )
        )
        self.secretary.groups.add(
            Group.objects.get(
                name=settings.GROUP_SECRETARY
            )
        )

        self.c1.groups.add(
            Group.objects.get(name=settings.GROUP_LINGUISTICS_CHAMBER)
        )
        self.c2.groups.add(
            Group.objects.get(name=settings.GROUP_LINGUISTICS_CHAMBER)
        )

    def setup_proposal(self):
        """
        Load our test proposals from a fixture, then add our user as
        an applicant to each of them.

        Please note, this currently uses a mish-mash of both fixtures
        and programmatically created users and objects.
        """
        self.proposal = Proposal.objects.get(pk=1)
        self.proposal.applicants.add(self.user)
        self.proposal.save()
        self.pre_assessment = Proposal.objects.get(pk=2)
        self.pre_assessment.applicants.add(self.user)
        self.pre_assessment.save()
        self.pre_approval = Proposal.objects.get(pk=3)
        self.pre_approval.applicants.add(self.user)
        self.pre_approval.save()

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

    def test_access(self,):
        # NB: The proposal creator does not have access by default
        # Be sure to add them to the applicants list as well.
        self.assertEqual(
            self.check_access(
                self.proposal.created_by,
            ),
            True
        )
        self.assertEqual(
            self.check_access(
                AnonymousUser,
            ),
            False
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
        self.assertIn(
            page.status_code,
            [302, 200]
        )
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
        self.assertIn(
            page.status_code,
            [302, 200]
        )
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


class PreapprovedSubmitTestCase(
        ProposalSubmitTestCase,
):
    view_class = ProposalSubmitPreApproved

    def setUp(self):
        super().setUp()
        self.proposal = self.pre_approval
