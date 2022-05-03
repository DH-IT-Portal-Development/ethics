from django import template


register = template.Library()


@register.filter(name='zip_equalize_lists')
def zip_equalize_lists(a, b):
    """
    A zip implementation which will not stop when reaching the end of the
    smallest list, but will append None's to the smaller list to fill the gap
    """
    a = list(a)
    b = list(b)
    a_len = len(a)
    b_len = len(b)
    diff = abs(a_len - b_len)

    if a_len < b_len:
        for _ in range(diff):
            a.append(None)

    if b_len < a_len:
        for _ in range(diff):
            b.append(None)

    return zip(a, b)


class ZippedSessionsNode(template.Node):
    """
    This node handles adding a zipped list of all sessions for 2 given studies
    If one study has more sessions than the other, None's will be added to
    the other
    """

    def __init__(self, var_name, study, p_study):
        self.var_name = var_name
        self.study = template.Variable(study)
        self.p_study = template.Variable(p_study)

    def render(self, context):
        study = self.study.resolve(context)
        p_study = self.p_study.resolve(context)

        sessions = []
        p_sessions = []

        if study:
            sessions = study.session_set.all()

        if p_study:
            p_sessions = p_study.session_set.all()

        context[self.var_name] = zip_equalize_lists(sessions, p_sessions)
        return u""


@register.tag
def get_zipped_sessions_lists(parser, token):
    """
    Adds a variable to the context with a zipped list of all sessions for
    the provided studies. If one study has more sessions than the other,
    None's will be added to the other

    Usage:
    {% get_zipped_sessions_lists VARIABLE_NAME STUDY_OBJECT_1 STUDY_OBJECT_2 %}
    params:
    VARIABLE_NAME: the name of the variable to store the object in
    STUDY_OBJECT_1: the variable which contains the first study object
    STUDY_OBJECT_2: the variable which contains the second study object
    """
    parts = token.split_contents()

    return ZippedSessionsNode(parts[1], parts[2], parts[3])


class ZippedTasksNode(template.Node):
    """
    This node handles adding a zipped list of all tasks for 2 given sessions
    If one session has more tasks than the other, None's will be added to
    the other
    """

    def __init__(self, var_name, session, p_session):
        self.var_name = var_name
        self.session = template.Variable(session)
        self.p_session = template.Variable(p_session)

    def render(self, context):
        session = self.session.resolve(context)
        p_session = self.p_session.resolve(context)

        tasks = []
        p_tasks = []

        if session:
            tasks = session.task_set.all()

        if p_session:
            p_tasks = p_session.task_set.all()

        context[self.var_name] = zip_equalize_lists(tasks, p_tasks)
        return u""


@register.tag
def get_zipped_tasks_lists(parser, token):
    """
    Adds a variable to the context with a zipped list of all tasks for
    the provided sessions. If one session has more tasks than the other,
    None's will be added to the other

    Usage:
    {% get_zipped_sessions_lists VARIABLE_NAME SESSION_OBJECT_1
    SESSION_OBJECT_2 %}
    params:
    VARIABLE_NAME: the name of the variable to store the object in
    SESSION_OBJECT_1: the variable which contains the first session object
    SESSION_OBJECT_2: the variable which contains the second session object
    """
    parts = token.split_contents()

    return ZippedTasksNode(parts[1], parts[2], parts[3])