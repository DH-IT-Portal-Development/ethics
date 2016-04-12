from .models import Proposal


def proposal_diffs(p1, p2):
    """
    Shows the differences for a Proposal.
    Copied from http://stackoverflow.com/a/31683045
    """
    my_model_fields = Proposal._meta.get_all_field_names()
    diffs = filter(lambda field: getattr(p1, field, None) != getattr(p2, field, None), my_model_fields)
    return diffs
