"""
This file contains code for validating a proposal by using all the relevant
forms and their validation code.

Used for the submit page, to check if a user has completed the proposal.
"""

from collections import OrderedDict

from braces.forms import UserKwargModelFormMixin

from interventions.forms import InterventionForm
from observations.forms import ObservationForm
from studies.forms import StudyForm, StudyDesignForm, SessionStartForm
from tasks.forms import TaskStartForm, TaskEndForm, TaskForm
from ..forms import (
    ProposalForm,
    WmoForm,
    StudyStartForm,
    WmoApplicationForm,
    TranslatedConsentForms,
    ProposalDataManagementForm,
)
from ..models import Proposal

from django.utils.translation import ugettext_lazy as _
from django.urls import reverse_lazy as reverse


def _build_forms(proposal: Proposal) -> OrderedDict:
    forms = OrderedDict()

    wmo_update_url = "proposals:wmo_update"
    wmo_application_url = "proposals:wmo_application"

    # Get the correct URL for the
    if proposal.is_pre_assessment:
        forms["start"] = (
            ProposalForm,
            reverse("proposals:update_pre", args=[proposal.pk]),
            _("Algemene informatie over de aanvraag"),
            proposal,
        )

        wmo_create_url = "proposals:wmo_create_pro"
        wmo_update_url = "proposals:wmo_update_pro"
    elif proposal.is_pre_approved:
        forms["start"] = (
            ProposalForm,
            reverse("proposals:update_pre_approved", args=[proposal.pk]),
            _("Algemene informatie over de aanvraag"),
            proposal,
        )
    elif proposal.is_practice():
        forms["start"] = (
            ProposalForm,
            reverse("proposals:update_practice", args=[proposal.pk]),
            _("Algemene informatie over de aanvraag"),
            proposal,
        )
    else:
        forms["start"] = (
            ProposalForm,
            reverse("proposals:update", args=[proposal.pk]),
            _("Algemene informatie over de aanvraag"),
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

        if study.has_sessions:
            taskbased_key = "{}_task_start".format(key_base)
            forms[taskbased_key] = (
                SessionStartForm,
                reverse("studies:session_start", args=[study.pk]),
                _("Het takenonderzoek (traject {})").format(
                    study.order,
                ),
                study,
            )

            for session in study.session_set.all():
                session_start_key = "{}_session_{}_start".format(
                    key_base,
                    session.pk,
                )

                forms[session_start_key] = (
                    TaskStartForm,
                    reverse("tasks:start", args=[session.pk]),
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
                    TaskEndForm,
                    reverse("tasks:end", args=[session.pk]),
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


def get_form_errors(proposal: Proposal) -> list:
    forms = _build_forms(proposal)

    troublesome_pages = []

    for key, form in forms.items():
        form_class, url, page_name, obj = form
        try:
            kwargs = {
                "instance": obj,
            }

            if issubclass(form_class, UserKwargModelFormMixin):
                # This is a bit ugly of course, as we should be getting the
                # authenticated used. But as only the owner will use this method,
                # it's the same thing.
                kwargs["user"] = proposal.created_by

            if issubclass(form_class, (StudyStartForm, StudyForm)):
                kwargs["proposal"] = proposal

            if issubclass(
                form_class, (InterventionForm, ObservationForm, TaskStartForm)
            ):
                kwargs["study"] = obj.study

            instance = form_class(**kwargs)

            for field, error in instance.errors.items():
                if field in instance.fields:
                    troublesome_pages.append(
                        {
                            "url": url,
                            "page_name": page_name,
                        }
                    )
                    break  # prevent duplicates for this field
        except:
            # If for some reason validation completely fails, we can assume
            # _something_ is not right and the page contains an error.
            troublesome_pages.append(
                {
                    "url": url,
                    "page_name": page_name,
                }
            )

    return troublesome_pages
