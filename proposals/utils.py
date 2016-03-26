from datetime import datetime

from django.contrib.auth import get_user_model

from .models import Proposal, AgeGroup


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


def get_users_as_list():
    """
    Retrieves all Users, excluding superusers, as a list.
    """
    users = get_user_model().objects.exclude(is_superuser=True)
    return [(user.pk, user.username + ': ' + user.get_full_name()) for user in users]


def check_necessity_required(proposal, age_groups, has_traits, legally_incapable):
    """
    This call checks whether the necessity questions are required. They are required when:
    - The researcher requires a supervisor AND one of these cases applies:
        - A selected AgeGroup requires details.
        - Participants have been selected on certain traits.
        - Participants are legally incapable.
    """
    if not proposal.relation.needs_supervisor:
        result = False
    else:
        required_values = AgeGroup.objects.filter(needs_details=True).values_list('id', flat=True)
        result = bool(set(required_values).intersection(age_groups))
        result |= has_traits
        result |= legally_incapable
    return result
