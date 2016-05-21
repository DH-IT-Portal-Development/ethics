from django import template
from django.apps import apps
from django.conf import settings
from django.contrib.auth.models import Group
from django.utils.safestring import mark_safe

from studies.utils import check_necessity_required

register = template.Library()


@register.simple_tag
def get_verbose_field_name(app_label, model_name, field_name, value=None):
    """
    Returns verbose_name for a field.
    """
    verbose_name = apps.get_model(app_label, model_name)._meta.get_field(field_name).verbose_name
    if value is not None:
        verbose_name %= value
    return verbose_name


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


@register.filter
def needs_details(selected_values, field='needs_details'):
    result = False
    for sv in selected_values:
        if getattr(sv, field):
            result = True
            break
    return result


@register.filter
def in_commission(current_user):
    """
    Check whether the current user is in the 'Commissie' group
    """
    return Group.objects.get(name=settings.GROUP_COMMISSION) in current_user.groups.all()


@register.filter
def necessity_required(study):
    age_groups = study.age_groups.values_list('id', flat=True)
    return check_necessity_required(study.proposal, age_groups, study.has_traits, study.legally_incapable)


@register.simple_tag
def show_all(app_label, model_name):
    """
    Return a unordered list of with all possible values for a model
    """
    result = '<ul>'
    for m in apps.get_model(app_label, model_name).objects.all():
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


@register.simple_tag
def show_yesnodoubt():
    return show_yesno(True)
