from django import template
from django.conf import settings
from django.contrib.auth.models import Group

register = template.Library()


@register.filter
def in_commission(current_user):
    """
    Check whether the current user is in the 'Commissie' group
    """
    return Group.objects.get(name=settings.GROUP_COMMISSION) in current_user.groups.all()
