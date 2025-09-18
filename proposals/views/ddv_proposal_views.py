from braces.views import LoginRequiredMixin
from cdh.vue3.components.uu_list import DDVListView, DDVString, DDVActions
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from proposals.api.ddv_views import (
    ProposalApiView,
    MyPracticeApiView,
    MySupervisedApiView,
)
from proposals.models import Proposal


class PrelabeledDDVColumn:
    reference_number = DDVString(
        field="reference_number",
        label="Ref.Num",
        css_classes="fw-bold text-danger",
    )
    title = DDVString(
        field="title",
        label="",
    )
    type = DDVString(
        field="type",
        label=_("Soort aanvraag"),
    )
    usernames = DDVString(
        field="usernames",
        label=_("Indieners"),
    )
    detailed_state = DDVString(
        field="detailed_state",
        label=_("Status"),
    )
    date_modified = DDVString(
        field="date_modified",
        label=_("Laatst bijgewerkt"),
    )
    date_submitted = DDVString(
        field="date_submitted",
        label=_("Datum ingediend"),
    )
    stage_display = DDVString(
        field="stage_display",
        label=_("Stadium"),
    )


class BaseDDVProposalView(
    LoginRequiredMixin,
    DDVListView,
):
    """title, data_uri, data_view, columns fields to be added for individual views"""

    model = Proposal
    template_name = "proposals/proposal_list.html"


class MyProposalsView(BaseDDVProposalView):
    title = _("Mijn aanvragen")
    data_view = ProposalApiView
    data_uri = reverse_lazy("proposals:api:my_proposals")
    columns = [
        PrelabeledDDVColumn.reference_number,
        PrelabeledDDVColumn.title,
        PrelabeledDDVColumn.type,
        PrelabeledDDVColumn.usernames,
        PrelabeledDDVColumn.detailed_state,
        PrelabeledDDVColumn.date_modified,
        PrelabeledDDVColumn.date_submitted,
        DDVActions(
            field="my_proposal_actions",
            label=_("Acties"),
        ),
    ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = self.title
        return context


class MyPracticeView(MyProposalsView):
    title = _("Mijn oefenaanvragen")
    data_uri = reverse_lazy("proposals:api:my_practice")
    data_view = MyPracticeApiView


class MySupervisedView(BaseDDVProposalView):
    title = _("Mijn aanvragen als eindverantwoordelijke")
    data_uri = reverse_lazy("proposals:api:my_supervised")
    data_view = MySupervisedApiView
    columns = [
        PrelabeledDDVColumn.reference_number,
        PrelabeledDDVColumn.title,
        PrelabeledDDVColumn.type,
        PrelabeledDDVColumn.usernames,
        PrelabeledDDVColumn.detailed_state,
        PrelabeledDDVColumn.date_modified,
        PrelabeledDDVColumn.date_submitted,
        PrelabeledDDVColumn.stage_display,
        DDVActions(
            field="my_supervised_actions",
            label=_("Acties"),
        ),
    ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = self.title
        return context
