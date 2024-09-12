"""
This file contains code for validating a proposal by using all the relevant
forms and their validation code. This is mostly handled by the Stepper, except
for sessions and tasks.

Used for the submit page, to check if a user has completed the proposal.
"""

from tasks.forms import SessionUpdateForm, SessionEndForm, TaskForm, SessionOverviewForm

from ..models import Proposal
from proposals.utils.stepper import Stepper

from django.utils.translation import gettext_lazy as _
from django.urls import reverse_lazy as reverse


def validate_sessions_tasks(study):
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
                    "page_name": _("{}: sessie {}").format(
                        study.name,
                        session.order,
                    ),
                }
            )
            for task in session.task_set.all():
                if TaskForm(instance=task).errors:
                    troublesome_session_pages.append(
                        {
                            "url": reverse("tasks:update", args=[task.pk]),
                            "page_name": _("{}: sessie {}, taak {}").format(
                                study.name,
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
                    "page_name": _("{}: sessie {} overzicht").format(
                        study.name,
                        session.order,
                    ),
                }
            )
    return troublesome_session_pages


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
