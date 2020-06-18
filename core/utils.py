from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
import django.utils.six as six

YES_NO = [(True, _('ja')), (False, _('nee'))]


class AvailableURL(object):
    def __init__(self, title, margin=0, url=None, is_title=False):
        self.title = title
        self.margin = margin
        self.url = url
        self.is_title = is_title


def get_secretary():
    """
    Returns the Head secretary. We limit this to one user.
    """
    obj = get_all_secretaries().first()
    obj.email = settings.EMAIL_FROM
    return obj

def get_all_secretaries():
    """
    Return all users in the 'Secretary' group.
    """
    return get_user_model().objects.filter(groups__name=settings.GROUP_HEAD_SECRETARY).all()

def is_secretary(user):
    """
    Check whether the current user is in the 'Secretary' group.
    """
    return Group.objects.get(name=settings.GROUP_SECRETARY) in user.groups.all()

def get_reviewers():
    return get_user_model().objects.filter(
        Q(groups__name=settings.GROUP_GENERAL_CHAMBER) |
        Q(groups__name=settings.GROUP_LINGUISTICS_CHAMBER)
    )


def get_reviewers_from_group(group):
    return get_user_model().objects.filter(
        groups__name=group
    )


def get_reviewers_from_groups(groups):
    return get_user_model().objects.filter(
        groups__name__in=groups
    )


def string_to_bool(s):
    if s == 'None' or s is None:
        return False
    return s not in ['False', 'false', '0', 0]


def get_users_as_list(users):
    """
    Retrieves all Users as a list.
    """
    return [(user.pk, u'{}: {}'.format(user.username, user.get_full_name())) for user in users]


def is_empty(value):
    """
    Checks if value is filled out (!= None).
    For lists and strings, also check if the value is not empty.
    """
    result = False
    if value is None:
        result = True
    if hasattr(value, '__len__') and len(value) == 0:
        result = True
    if isinstance(value, six.text_type) and not value.strip():
        result = True
    return result
