from __future__ import division

from django.urls import reverse
from django.utils.translation import gettext as _

from main.utils import AvailableURL

SESSION_PROGRESS_START = 10
SESSION_PROGRESS_TOTAL = 20
SESSION_PROGRESS_EPSILON = 5


def get_session_progress(session, is_end=False):
    from studies.utils import get_study_progress
    progress = SESSION_PROGRESS_TOTAL / session.study.sessions_number
    if not is_end:
        progress *= (session.order - 1)
    else:
        progress *= session.order
    return int(get_study_progress(session.study) + SESSION_PROGRESS_START + progress)


def get_task_progress(task):
    session = task.session
    session_progress = get_session_progress(session)
    task_progress = task.order / session.tasks_number
    return int(session_progress + (SESSION_PROGRESS_TOTAL / session.study.sessions_number) * task_progress - SESSION_PROGRESS_EPSILON)


def session_urls(study, troublesome_urls):

    tasks_url = AvailableURL(title=_('Takenonderzoek'))

    if study.has_sessions:
        tasks_url.url = reverse('studies:session_start', args=(study.pk,))
        tasks_url.has_errors = tasks_url.has_errors in troublesome_urls

    if study.has_sessions:
        prev_session_completed = True
        for session in study.session_set.all():
            task_start_url = AvailableURL(title=_('Sessie {}').format(session.order))
            if prev_session_completed:
                task_start_url.url = reverse('tasks:start', args=(session.pk,))
                task_start_url.has_errors = task_start_url.url in troublesome_urls
            tasks_url.children.append(task_start_url)

            task_start_url.children.extend(tasks_urls(session, troublesome_urls))

            task_end_url = AvailableURL(title=_('Overzicht'))
            if session.tasks_completed():
                task_end_url.url = reverse('tasks:end', args=(session.pk,))
                task_end_url.has_errors = task_end_url.url in troublesome_urls
            task_start_url.children.append(task_end_url)

            prev_session_completed = session.is_completed()

    return tasks_url


def tasks_urls(session, troublesome_urls):
    result = list()

    prev_task_completed = True
    for task in session.task_set.all():
        task_url = AvailableURL(title=_('Taak {}').format(task.order))
        if prev_task_completed:
            task_url.url = reverse('tasks:update', args=(task.pk,))
            task_url.has_errors = task_url.url in troublesome_urls
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
    t.registration_kinds.set(
        original_task.registration_kinds.all()
    )
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
