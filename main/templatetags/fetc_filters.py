from django import template
from django.conf import settings
from django.contrib.auth.models import Group

register = template.Library()


@register.filter
def in_linguistics_chamber(current_user):
    """
    Check whether the current user is in the 'ETCL' or 'Secretaris' group
    """
    return Group.objects.get(name=settings.GROUP_LINGUISTICS_CHAMBER) in current_user.groups.all() or \
           Group.objects.get(name=settings.GROUP_SECRETARY) in current_user.groups.all()


@register.filter
def in_general_chamber(current_user):
    """
    Check whether the current user is in the 'FETC' or 'Secretaris' group
    """
    return Group.objects.get(name=settings.GROUP_GENERAL_CHAMBER) in current_user.groups.all() or \
           Group.objects.get(name=settings.GROUP_SECRETARY) in current_user.groups.all()


@register.filter
def is_secretary(current_user):
    """
    Check whether the current user is in the 'Secretary' group
    """
    return Group.objects.get(name=settings.GROUP_SECRETARY) in current_user.groups.all()

@register.filter
def is_chair_or_secretary(current_user):
    """
    Check whether the current user is in the 'Chair' or 'Secretary' Group
    """
    user_groups = current_user.groups.all()
    return (
        Group.objects.get(name=settings.GROUP_CHAIR) in user_groups
        or Group.objects.get(name=settings.GROUP_SECRETARY) in user_groups
    )
