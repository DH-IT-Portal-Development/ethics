from datetime import date

from django.contrib.auth.models import User, Group, AnonymousUser
from django.conf import settings
from django.test import TestCase

from main.tests import BaseViewTestCase
from main.models import Setting, YES, NO
from proposals.models import Proposal, Wmo, Relation
from studies.models import Study, Compensation
from proposals.utils import generate_ref_number

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

        self.proposal = Proposal.objects.create(
            title='p1', reference_number=generate_ref_number(),
            date_start=date.today(),
            created_by=self.user,
            supervisor=self.supervisor,
            relation=Relation.objects.get(pk=4),
            reviewing_committee=Group.objects.get(
                name=settings.GROUP_LINGUISTICS_CHAMBER
            ),
            institution_id=1,
        )
        self.proposal.applicants.add(self.user)
        self.proposal.save()
        self.proposal.wmo = Wmo.objects.create(
            proposal=self.proposal,
            metc=NO,
        )
        self.study = Study.objects.create(
            proposal=self.proposal,
            order=1,
            compensation=Compensation.objects.get(
                pk=2,
            )
        )

    def refresh(self):
        """Refresh objects from DB. This is sometimes necessary if you access
        attributes you previously read during the test and don't want to
        receive a cached value."""
        self.proposal.refresh_from_db()


class BaseProposalSubmitTestCase(
        BaseViewTestCase,
        BaseProposalTestCase,
):
    view_class = ProposalSubmit

    def get_view_path(self):
        pk = self.proposal.pk
        return f"/proposals/submit/{pk}/"

    def get_view_args(self):
        return {"pk": self.proposal.pk}

    def test_access(self,):
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

    def test_submission(self):
        self.assertEqual(
            self.proposal.status,
            self.proposal.DRAFT,
        )
        self.client.force_login(self.proposal.created_by)
        form_values = {}
        page = self.post(form_values)
        self.refresh()
        self.assertNotEqual(
            self.proposal.status,
            self.proposal.DRAFT,
        )
