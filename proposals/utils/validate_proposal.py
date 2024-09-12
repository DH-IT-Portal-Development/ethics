"""
This file contains code for validating a proposal by using all the relevant
forms and their validation code.

Used for the submit page, to check if a user has completed the proposal.
"""

from collections import OrderedDict

from braces.forms import UserKwargModelFormMixin

from interventions.forms import InterventionForm
from observations.forms import ObservationForm
from studies.forms import StudyForm, StudyDesignForm, StudyEndForm
from tasks.forms import SessionUpdateForm, SessionEndForm, TaskForm, SessionOverviewForm

from ..models import Proposal
from proposals.utils.stepper import Stepper

from django.utils.translation import gettext_lazy as _
from django.urls import reverse_lazy as reverse


def _build_forms(proposal: Proposal) -> OrderedDict:
    forms = OrderedDict()

    wmo_update_url = "proposals:wmo_update"
    wmo_application_url = "proposals:wmo_application"

    forms["start"] = (
        ProposalForm,
        reverse("proposals:update", args=[proposal.pk]),
        _("Algemene informatie over de aanvraag"),
        proposal,
    )

    forms["Researcher"] = (
        ResearcherForm,
        reverse("proposals:researcher", args=[proposal.pk]),
        _("Informatie over de onderzoeker"),
        proposal,
    )

    forms["OtherResearchers"] = (
        OtherResearchersForm,
        reverse("proposals:other_researchers", args=[proposal.pk]),
        _("Informatie over betrokken onderzoekers"),
        proposal,
    )

    if not proposal.is_pre_assessment:
        forms["Funding"] = (
            FundingForm,
            reverse("proposals:funding", args=[proposal.pk]),
            _("Informatie over financiering"),
            proposal,
        )

    forms["ResearchGoal"] = (
        ResearchGoalForm,
        reverse("proposals:research_goal", args=[proposal.pk]),
        _("Informatie over het onderzoeksdoel"),
        proposal,
    )

    if proposal.is_pre_assessment:
        wmo_update_url = "proposals:wmo_update_pre"

    if proposal.is_pre_approved:
        forms["PreApproved"] = (
            PreApprovedForm,
            reverse("proposals:pre_approved", args=[proposal.pk]),
            _("Informatie over eerdere toetsing"),
            proposal,
        )

    # For pre approved proposals, we're done already!
    if proposal.is_pre_approved:
        return forms

    if hasattr(proposal, "wmo"):
        forms["wmo_form"] = (
            WmoForm,
            reverse(wmo_update_url, args=[proposal.wmo.pk]),
            _("Ethische toetsing nodig door een METC?"),
            proposal.wmo,
        )
        if proposal.wmo.status != proposal.wmo.WMOStatuses.NO_WMO:
            forms["wmo_application"] = (
                WmoApplicationForm,
                reverse(wmo_application_url, args=[proposal.pk]),
                _("Ethische toetsing nodig door een METC?"),
                proposal.wmo,
            )

    # Now we're done for pre assessment proposals
    if proposal.is_pre_assessment:
        return forms

    forms["study_start"] = (
        StudyStartForm,
        reverse("proposals:study_start", args=[proposal.pk]),
        _("Eén of meerdere trajecten?"),
        proposal,
    )

    for study in proposal.study_set.all():
        key_base = "study_{}".format(study.pk)

        start_key = "{}_start".format(key_base)
        forms[start_key] = (
            StudyForm,
            reverse("studies:update", args=[study.pk]),
            _("De deelnemers (traject {})").format(study.order),
            study,
        )

        design_key = "{}_design".format(key_base)
        forms[design_key] = (
            StudyDesignForm,
            reverse("studies:design", args=[study.pk]),
            _("De onderzoekstype(n) (traject {})").format(study.order),
            study,
        )

        end_key = "{}_end".format(key_base)
        forms[end_key] = (
            StudyEndForm,
            reverse("studies:design_end", args=[study.pk]),
            _("Trajectoverzicht (traject {})").format(study.order),
            study,
        )

        if study.has_intervention:
            intervention_key = "{}_intervention".format(key_base)
            if hasattr(study, "intervention"):
                forms[intervention_key] = (
                    InterventionForm,
                    reverse("interventions:update", args=[study.intervention.pk]),
                    _("Het interventieonderzoek (traject {})").format(
                        study.order,
                    ),
                    study.intervention,
                )
            else:
                forms[intervention_key] = (
                    InterventionForm,
                    reverse("interventions:create", args=[study.pk]),
                    _("Het interventieonderzoek (traject {})").format(
                        study.order,
                    ),
                    None,
                )

        if study.has_observation:
            observation_key = "{}_observation".format(key_base)
            if hasattr(study, "observation"):
                forms[observation_key] = (
                    ObservationForm,
                    reverse("observations:update", args=[study.observation.pk]),
                    _("Het observatieonderzoek (traject {})").format(
                        study.order,
                    ),
                    study.observation,
                )
            else:
                forms[observation_key] = (
                    ObservationForm,
                    reverse("observations:create", args=[study.pk]),
                    _("Het observatieonderzoek (traject {})").format(
                        study.order,
                    ),
                    None,
                )

        if study.has_no_sessions():
            session_overview_key = "{}_session_overview".format(
                key_base,
            )
            forms[session_overview_key] = (
                SessionOverviewForm,
                reverse(
                    "tasks:session_overview",
                    args=[
                        study.pk,
                    ],
                ),
                _("Overzicht van het takenonderzoek (traject {})").format(
                    study.order,
                ),
                study,
            )
        elif study.has_sessions:
            for session in study.session_set.all():
                session_start_key = "{}_session_{}_start".format(
                    key_base,
                    session.pk,
                )

                forms[session_start_key] = (
                    SessionUpdateForm,
                    reverse("tasks:session_update", args=[session.pk]),
                    _("Het takenonderzoek: sessie {} (traject {})").format(
                        session.order,
                        study.order,
                    ),
                    session,
                )

                for task in session.task_set.all():
                    task_key = "{}_session_{}_task_{}".format(
                        key_base,
                        session.pk,
                        task.pk,
                    )

                    forms[task_key] = (
                        TaskForm,
                        reverse("tasks:update", args=[task.pk]),
                        _("Het takenonderzoek: sessie {} taak {} (traject {})").format(
                            session.order,
                            task.order,
                            study.order,
                        ),
                        task,
                    )

                session_end_key = "{}_session_{}_end".format(
                    key_base,
                    session.pk,
                    session,
                )

                forms[session_end_key] = (
                    SessionEndForm,
                    reverse("tasks:session_end", args=[session.pk]),
                    _("Overzicht van takenonderzoek: sessie {} (traject {})").format(
                        session.order,
                        study.order,
                    ),
                    session,
                )

    forms["translated"] = (
        TranslatedConsentForms,
        reverse("proposals:translated", args=[proposal.pk]),
        _("Vertaling informed consent formulieren"),
        proposal,
    )

    forms["data_management"] = (
        ProposalDataManagementForm,
        reverse("proposals:data_management", args=[proposal.pk]),
        _("AVG en Data Management"),
        proposal,
    )

    return forms


def get_form_errors(stepper: Stepper) -> list:

    troublesome_pages = []
    study_titles = [study.name for study in stepper.proposal.study_set.all()]

    for item in stepper.items:
        if hasattr(item, "form_class") and item.form_class == SessionOverviewForm:
            troublesome_pages.extend(validate_sessions_tasks(item.study))
        if item.get_errors():
            if item.parent and item.parent.title in study_titles:
                page_name = f"{item.parent.title}: {item.title}"
            else:
                page_name = item.title
            troublesome_pages.append(
                {
                    "url": item.get_url(),
                    "page_name": page_name,
                }
            )

    return troublesome_pages
