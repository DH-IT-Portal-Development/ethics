from __future__ import division

from django.urls import reverse
from django.utils.translation import ugettext as _

from main.utils import AvailableURL


def session_urls(study):
    tasks_url = AvailableURL(title=_("Takenonderzoek"))

    if study.has_sessions:
        tasks_url.url = reverse("tasks:session_start", args=(study.pk,))

    if study.has_sessions:
        prev_session_completed = True
        for session in study.session_set.all():
            task_start_url = AvailableURL(
                title=_("Het takenonderzoek: sessie {}").format(session.order)
            )
            if prev_session_completed:
                task_start_url.url = reverse("tasks:session_update", args=(session.pk,))
            tasks_url.children.append(task_start_url)

            tasks_url.children.extend(tasks_urls(session))

            task_end_url = AvailableURL(
                title=_("Overzicht van takenonderzoek: sessie {}").format(session.order)
            )
            if session.tasks_completed():
                task_end_url.url = reverse("tasks:session_end", args=(session.pk,))
            tasks_url.children.append(task_end_url)

            prev_session_completed = session.is_completed()

    return tasks_url


def tasks_urls(session):
    result = list()

    prev_task_completed = True
    for task in session.task_set.all():
        task_url = AvailableURL(
            title=_("Het takenonderzoek: sessie {} taak {}").format(
                session.order, task.order
            )
        )
        if prev_task_completed:
            task_url.url = reverse("tasks:update", args=(task.pk,))
        result.append(task_url)

        prev_task_completed = task.is_completed()

    return result


def copy_task_to_session(session, original_task):
    from tasks.models import Task

    t = Task.objects.get(pk=original_task.pk)
    t.pk = None
    t.session = session
    t.save()

    t.registrations.set(original_task.registrations.all())
    t.registration_kinds.set(original_task.registration_kinds.all())
    t.save()


def copy_session_to_study(study, original_session):
    from tasks.models import Session

    s = Session.objects.get(pk=original_session.pk)
    s.pk = None
    s.study = study
    s.save()

    s.setting.set(original_session.setting.all())
    s.save()

    for task in original_session.task_set.all():
        copy_task_to_session(s, task)
