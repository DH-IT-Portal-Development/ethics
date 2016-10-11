from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext as _

YES_NO = [(True, _('ja')), (False, _('nee'))]


class AvailableURL(object):
    def __init__(self, title, margin=0, url=None, is_title=False):
        self.title = title
        self.margin = margin
        self.url = url
        self.is_title = is_title


def get_secretary():
    """
    Returns the Secretary. We limit this to one user.
    """
    return get_user_model().objects.filter(groups__name=settings.GROUP_SECRETARY)[0]


def get_reviewers():
    return get_user_model().objects.filter(groups__name=settings.GROUP_COMMISSION)


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
    For unicode strings, also check if the value is not empty.
    """
    result = False
    if value is None:
        result = True
    if isinstance(value, unicode) and not value.strip():
        result = True
    return result
