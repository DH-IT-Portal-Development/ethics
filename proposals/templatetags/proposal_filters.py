from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def get_verbose_field_name(instance, field_name):
    """
    Returns verbose_name for a field.
    """
    return instance._meta.get_field(field_name).verbose_name


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
