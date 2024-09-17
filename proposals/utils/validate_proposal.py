"""
This file contains code for validating a proposal by using all the relevant
forms and their validation code. This is mostly handled by the Stepper, except
for sessions and tasks.

Used for the submit page, to check if a user has completed the proposal.
"""

from tasks.forms import SessionUpdateForm, SessionEndForm, TaskForm, SessionOverviewForm
from studies.forms import StudyForm, StudyDesignForm, StudyEndForm
from observations.forms import ObservationForm
from interventions.forms import InterventionForm

from ..models import Proposal
from proposals.utils.stepper import Stepper

from django.utils.translation import gettext_lazy as _
from django.urls import reverse_lazy as reverse


def validate_sessions_tasks(study, multiple_studies):
    """As we do currently not have individual tasks and sessions in the
    stepper, these forms get instantiated and checked for errors separately
    in this function."""

    troublesome_session_pages = []

    for session in study.session_set.all():
        # Check if errors in instantiated form
        if SessionUpdateForm(instance=session, study=study).errors:
            # if so, append dict, with url and formatted page name
            troublesome_session_pages.append(
                {
                    "url": reverse("tasks:session_update", args=[session.pk]),
                    "page_name": _("Sessie {}").format(
                        session.order,
                    ),
                }
            )
            for task in session.task_set.all():
                if TaskForm(instance=task).errors:
                    troublesome_session_pages.append(
                        {
                            "url": reverse("tasks:update", args=[task.pk]),
                            "page_name": _("Sessie {}, taak {}").format(
                                session.order,
                                task.order,
                            ),
                        }
                    )
        if SessionEndForm(instance=session).errors:
            # if so, append tuple, with url and formatted page name
            troublesome_session_pages.append(
                {
                    "url": reverse("tasks:session_end", args=[session.pk]),
                    "page_name": _("Sessie {} overzicht").format(
                        session.order,
                    ),
                }
            )
            
    if multiple_studies:
        for dict in troublesome_session_pages:
            dict["page_name"] = "{}: {}".format(
                study.name,
                dict["page_name"],
            )
    return troublesome_session_pages


def get_form_errors(stepper: Stepper) -> list:

    troublesome_pages = []
    study_forms = [StudyForm, StudyEndForm, StudyDesignForm, InterventionForm, ObservationForm, SessionOverviewForm]
    multiple_studies = len(stepper.proposal.study_set.all()) > 1 

    for item in stepper.items:
        if hasattr(item, "form_class") and item.form_class == SessionOverviewForm:
            troublesome_pages.extend(validate_sessions_tasks(item.study, multiple_studies))
        if item.get_errors():
            if multiple_studies and item.form_class in study_forms:
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
