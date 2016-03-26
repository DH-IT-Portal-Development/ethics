# -*- encoding: utf-8 -*-

from django.apps import apps
from django.http import JsonResponse
from django.views import generic
from django.views.decorators.csrf import csrf_exempt


# Home view
class HomeView(generic.TemplateView):
    template_name = 'proposals/index.html'


################
# AJAX callbacks
################
@csrf_exempt
def check_requires(request):
    """
    This call checks whether a certain value requires another input to be filled.
    """
    values = map(int, request.POST.getlist('value[]'))
    model = apps.get_model(request.POST.get('app'), request.POST.get('model'))
    required_values = model.objects.filter(**{request.POST.get('field'): True}).values_list('id', flat=True)
    result = bool(set(required_values).intersection(values))
    return JsonResponse({'result': result})
