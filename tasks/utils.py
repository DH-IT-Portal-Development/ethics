from __future__ import division


def copy_task_to_session(session, original_task):
    from tasks.models import Task

    t = Task.objects.get(pk=original_task.pk)
    t.pk = None
    t.session = session
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
