from .models import AgeGroup

STUDY_PROGRESS_START = 10
STUDY_PROGRESS_TOTAL = 80


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


def get_study_progress(study, is_end=False):
    if not study:
        return STUDY_PROGRESS_START
    progress = STUDY_PROGRESS_TOTAL / study.proposal.studies_number
    if not is_end:
        progress *= (study.order - 1)
    else:
        progress *= study.order
    return STUDY_PROGRESS_START + progress
