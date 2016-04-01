from django.utils.translation import ugettext as _

YES_NO = [(True, _('ja')), (False, _('nee'))]
YES_NO_DOUBT = [(True, _('ja')), (False, _('nee')), (None, _('twijfel'))]


def string_to_bool(s):
    if s == 'None':
        return None
    return s not in ['False', 'false', '0', 0]
