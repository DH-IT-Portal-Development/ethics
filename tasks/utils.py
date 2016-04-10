SESSION_PROGRESS_START = 35
SESSION_PROGRESS_TOTAL = 50
SESSION_PROGRESS_EPSILON = 5


def get_session_progress(session, is_end=False):
    progress = SESSION_PROGRESS_TOTAL / session.study.sessions_number
    if not is_end:
        progress *= (session.order - 1)
    else:
        progress *= session.order
    return SESSION_PROGRESS_START + progress


def get_task_progress(task):
    session = task.session
    session_progress = get_session_progress(session)
    task_progress = task.order / float(session.tasks_number)
    return int(session_progress + (SESSION_PROGRESS_TOTAL / session.study.sessions_number) * task_progress - SESSION_PROGRESS_EPSILON)


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
    tasks = session.tasks.all()

    s = session
    s.pk = None
    s.study = study
    s.save()

    for task in tasks:
        copy_task_to_session(s, task)
