from django import template
from django.apps import apps
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def get_verbose_field_name(instance, field_name):
    """
    Returns verbose_name for a field.
    """
    return apps.get_model('proposals', instance)._meta.get_field(field_name).verbose_name


@register.filter
def show_selected(selected_values):
    """
    Return a unordered list of with all possible values for a model,
    with the selected ones in bold.
    """
    result = '<ul>'
    model = type(selected_values[0])
    for m in model.objects.all():
        if m in selected_values:
            result += '<li><strong>{}</strong></li>'.format(str(m))
        else:
            result += '<li>{}</li>'.format(str(m))
    result += '</ul>'
    return mark_safe(result)


@register.simple_tag
def show_all(model):
    """
    Return a unordered list of with all possible values for a model
    """
    result = '<ul>'
    for m in apps.get_model('proposals', model).objects.all():
        result += '<li>{}</li>'.format(str(m))
    result += '</ul>'
    return mark_safe(result)


@register.simple_tag
def show_yesno(doubt=False):
    result = '<ul>'
    result += '<li>{}</li>'.format('ja')
    result += '<li>{}</li>'.format('nee')
    if doubt:
        result += '<li>{}</li>'.format('twijfel')
    result += '</ul>'
    return mark_safe(result)
