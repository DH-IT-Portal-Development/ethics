from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext as _

YES_NO = [(True, _('ja')), (False, _('nee'))]


def get_secretary():
    """
    Returns the Secretary. We limit this to one user.
    """
    return get_user_model().objects.filter(groups__name=settings.GROUP_SECRETARY)[0]


def string_to_bool(s):
    if s == 'None':
        return None
    return s not in ['False', 'false', '0', 0]


def get_users_as_list(users):
    """
    Retrieves all Users as a list.
    """
    return [(user.pk, u'{}: {}'.format(user.username, user.get_full_name())) for user in users]
