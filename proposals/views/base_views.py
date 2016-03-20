# -*- encoding: utf-8 -*-

from django.apps import apps
from django.core.urlresolvers import reverse
from django.http import JsonResponse
from django.views import generic
from django.views.decorators.csrf import csrf_exempt

SESSION_PROGRESS_START = 35
SESSION_PROGRESS_TOTAL = 50
SESSION_PROGRESS_EPSILON = 5


# Home view
class HomeView(generic.TemplateView):
    template_name = 'proposals/index.html'

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        return context


################
# AJAX callbacks
################
@csrf_exempt
def check_requires(request):
    """
    This call checks whether a certain value requires another input to be filled.
    """
    values = map(int, request.POST.getlist('value[]'))
    model = apps.get_model('proposals', request.POST.get('model'))
    required_values = model.objects.filter(**{request.POST.get('field'): True}).values_list('id', flat=True)
    result = bool(set(required_values).intersection(values))
    return JsonResponse({'result': result})


#########
# Helpers
#########
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
