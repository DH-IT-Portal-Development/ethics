from datetime import datetime

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
    print 'value is ', s
    if s == 'None':
        return None
    elif s in ['False', 'false', '0', 0]:
        return False
    else:
        return True
