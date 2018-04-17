from __future__ import division

from django.urls import reverse
from django.utils.translation import ugettext as _

from core.utils import AvailableURL

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


def session_urls(study):
    urls = list()

    tasks_url = AvailableURL(title=_('Het takenonderzoek'), margin=2)

    if study.has_sessions:
        tasks_url.url = reverse('studies:session_start', args=(study.pk,))
    urls.append(tasks_url)

    if study.has_sessions:
        prev_session_completed = True
        for session in study.session_set.all():
            task_start_url = AvailableURL(title=_('Het takenonderzoek: sessie {}').format(session.order), margin=3)
            if prev_session_completed:
                task_start_url.url = reverse('tasks:start', args=(session.pk,))
            urls.append(task_start_url)

            urls.extend(tasks_urls(session))

            task_end_url = AvailableURL(title=_('Overzicht van takenonderzoek: sessie {}').format(session.order), margin=3)
            if session.tasks_completed():
                task_end_url.url = reverse('tasks:end', args=(session.pk,))
            urls.append(task_end_url)

            prev_session_completed = session.is_completed()

    return urls


def tasks_urls(session):
    result = list()

    prev_task_completed = True
    for task in session.task_set.all():
        task_url = AvailableURL(title=_('Het takenonderzoek: sessie {} taak {}').format(session.order, task.order), margin=3)
        if prev_task_completed:
            task_url.url = reverse('tasks:update', args=(task.pk,))
        result.append(task_url)

        prev_task_completed = task.is_completed()

    return result


def copy_task_to_session(session, task):
    r = task.registrations.all()
    rk = task.registration_kinds.all()

    t = task
    t.pk = None
    t.session = session
    t.save()

    t.registrations = r
    t.registration_kinds = rk
    t.save()


def copy_session_to_study(study, session):
    setting = session.setting.all()
    tasks = session.task_set.all()

    s = session
    s.pk = None
    s.study = study
    s.save()

    s.setting = setting
    s.save()

    for task in tasks:
        copy_task_to_session(s, task)
