from django.contrib.auth import get_user_model
from django.utils.translation import ugettext as _
from django.utils import timezone

from .models import Review, Decision
from proposals.models import Task


def start_review(proposal):
    """
    Starts a Review for the given Proposal.

    If the proposal has a supervisor:
    - Set the review status to SUPERVISOR
    - Set date_submitted_supervisor to current date/time
    - (TODO) Send an e-mail to the supervisor

    If the proposal has no supervisor:
    - Set the review status to ASSIGNMENT
    - Set date_submitted to current date/time
    - (TODO) Send an e-mail to the superusers
    """
    review = Review.objects.create(proposal=proposal, date_start=timezone.now())

    if proposal.relation.needs_supervisor:
        review.stage = Review.SUPERVISOR
        review.save()

        proposal.date_submitted_supervisor = timezone.now()
        proposal.save()

        decision = Decision(review=review, reviewer=proposal.supervisor)
        decision.save()
    else:
        review.stage = Review.ASSIGNMENT
        review.save()

        proposal.date_submitted = timezone.now()
        proposal.save()

        for user in get_user_model().objects.filter(is_superuser=True):
            decision = Decision(review=review, reviewer=user)
            decision.save()

    return review


def auto_review(proposal):
    go = True
    reasons = []

    if proposal.sessions_stressful or proposal.sessions_stressful is None:
        go = False
        reasons.append(_('Een onderdeel van de procedure kan belastend worden ervaren.'))

    for age_group in proposal.study.age_groups.all():
        if age_group.needs_details and not proposal.study.necessity:
            go = False
            reasons.append(_('Het is niet noodzakelijk deze groep proefpersonen te gebruiken'))

        if proposal.net_duration() > age_group.max_net_duration:
            go = False
            reasons.append(_('Overschrijdt maximale duratie voor leeftijdsgroep {}'.format(age_group)))

    for setting in proposal.study.setting.all():
        if setting.needs_details:
            go = False
            reasons.append(_('De dataverzameling vindt op een ongebruikelijke plek plaats: {}').format(proposal.study.setting_details))

    for task in Task.objects.filter(session__proposal=proposal):
        for registration in task.registrations.all():
            if registration.requires_review:
                go = False
                reasons.append(_('Taak {} in sessie {} legt gegevens vast via {}').format(task.name, task.session.order, registration.description))

    if proposal.study.risk_physical:
        go = False
        reasons.append(_('Verhoogd risico op fysieke schade'))

    if proposal.study.risk_psychological:
        go = False
        reasons.append(_('Verhoogd risico op psychische schade'))

    if proposal.study.compensation.requires_review:
        go = False
        reasons.append(_('Afwijkende vorm van compensatie'))

    return go, reasons
