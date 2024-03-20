from django import template
from django.conf import settings
from django.contrib.auth.models import Group

register = template.Library()


def is_in_groups(current_user, groups):
    """
    Check whether the current user is in specific groups, specified in the
    groups argument, like eg.:

    groups = [settings.GROUP_SECRETARY, settings.GROUP_CHAIR]
    """
    user_groups = current_user.groups.all()
    group_objects = [Group.objects.get(name=group) for group in groups]

    return any(group in user_groups for group in group_objects)


@register.filter
def in_linguistics_chamber(current_user):
    """
    Check whether the current user is in the 'ETCL' or 'Secretaris' group
    """
    return is_in_groups(
        current_user, [settings.GROUP_LINGUISTICS_CHAMBER, settings.GROUP_SECRETARY]
    )


@register.filter
def in_general_chamber(current_user):
    """
    Check whether the current user is in the 'FETC' or 'Secretaris' group
    """
    return is_in_groups(
        current_user, [settings.GROUP_GENERAL_CHAMBER, settings.GROUP_SECRETARY]
    )


@register.filter
def is_secretary(current_user):
    """
    Check whether the current user is in the 'Secretary' group
    """
    return is_in_groups(current_user, [settings.GROUP_SECRETARY])


@register.filter
def is_chair_or_secretary(current_user):
    """
    Check whether the current user is in the 'Secretary' or 'Chair' group
    """
    return is_in_groups(current_user, [settings.GROUP_SECRETARY, settings.GROUP_CHAIR])


@register.filter
def is_po_chair_or_secretary(current_user):
    """
    Check whether the current user is in the 'Secretary', 'Privacy officer'
    or 'Chair' group
    """
    return is_in_groups(
        current_user,
        [settings.GROUP_SECRETARY, settings.GROUP_CHAIR, settings.GROUP_PO],
    )
