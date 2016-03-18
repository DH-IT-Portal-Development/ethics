from datetime import datetime

from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext as _

from .models import Proposal


def generate_ref_number(user):
    current_year = datetime.now().year
    try:
        last_proposal = Proposal.objects.filter(created_by=user).filter(date_created__year=current_year).latest('date_created')
        proposal_number = int(last_proposal.reference_number.split('-')[1]) + 1
    except Proposal.DoesNotExist:
        proposal_number = 1

    return '{}-{:02}-{}'.format(user.username, proposal_number, current_year)


def string_to_bool(s):
    if s == 'None':
        return None
    return s not in ['False', 'false', '0', 0]


def check_dependency(form, cleaned_data, f1, f2, error_message=''):
    is_required = False
    if not error_message:
        error_message = _('Dit veld is verplicht.')
    if cleaned_data.get(f1) and not cleaned_data.get(f2):
        is_required = True
        form.add_error(f2, forms.ValidationError(error_message, code='required'))
    return is_required


def check_dependency_singular(form, cleaned_data, f1, f1_field, f2, error_message=''):
    is_required = False
    if not error_message:
        error_message = _('Dit veld is verplicht.')
    if cleaned_data.get(f1):
        if getattr(cleaned_data.get(f1), f1_field) and not cleaned_data.get(f2):
            is_required = True
            form.add_error(f2, forms.ValidationError(error_message, code='required'))
    return is_required


def check_dependency_multiple(form, cleaned_data, f1, f1_field, f2, error_message=''):
    is_required = False
    if not error_message:
        error_message = _('Dit veld is verplicht.')
    if cleaned_data.get(f1):
        for item in cleaned_data.get(f1):
            if getattr(item, f1_field) and not cleaned_data.get(f2):
                is_required = True
                form.add_error(f2, forms.ValidationError(error_message, code='required'))
                break
    return is_required


def get_users_as_list():
    """
    Retrieves all Users, excluding superusers, as a list.
    """
    users = get_user_model().objects.exclude(is_superuser=True)
    return [(user.pk, user.username + ': ' + user.get_full_name()) for user in users]
