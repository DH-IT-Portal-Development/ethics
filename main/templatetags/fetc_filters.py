from django import template
from django.conf import settings
from django.contrib.auth.models import Group
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

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


@register.filter
def create_unordered_html_list(lst):
    html_output = mark_safe('<p class="p-0">')

    for index, item in enumerate(lst):
        html_output += format_html("• {}", item)
        if index != len(lst) - 1:
            html_output += mark_safe("<br/>")

    html_output += mark_safe("</p>")

    return html_output

@register.filter
def unknown_if_none(value):
    return value if value is not None else _("Onbekend aantal")