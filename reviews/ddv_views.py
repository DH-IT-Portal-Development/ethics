from braces.views import GroupRequiredMixin
from django.conf import settings
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from proposals.views.ddv_proposal_views import MyProposalsView
from reviews.api.ddv_views import MySecretaryApiView
from reviews.mixins import CommitteeMixin


class MySecretaryView(GroupRequiredMixin, CommitteeMixin, MyProposalsView):
    title = _("Alle ingezonden aanvragen")
    group_required = (settings.GROUP_SECRETARY, settings.GROUP_CHAIR, settings.GROUP_PO)

    data_view = MySecretaryApiView

    def get_d(self):
        return self.committee

    data_uri = reverse("reviews:api:archive", args=[get_d])

    def get_group_required(self):
        # Depending on committee kwarg we test for the correct group
        group_required = [
            settings.GROUP_SECRETARY,
            settings.GROUP_CHAIR,
            settings.GROUP_PO,
        ]

        if self.committee.name == "AK":
            group_required += [settings.GROUP_GENERAL_CHAMBER]
        if self.committee.name == "LK":
            group_required += [settings.GROUP_LINGUISTICS_CHAMBER]

        return group_required
