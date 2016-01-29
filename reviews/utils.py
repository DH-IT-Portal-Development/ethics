from django.contrib.auth import get_user_model
from django.utils.translation import ugettext as _
from django.utils import timezone

from .models import Review, Decision
from proposals.models import Task

SECRETARY = 'Secretaris'


def start_review(proposal):
    """
    Starts a Review for the given Proposal.

    If the proposal needs a supervisor, start the supervisor phase. Otherwise, start the assignment phase.
    """
    if proposal.relation.needs_supervisor:
        review = start_supervisor_phase(proposal)
    else:
        review = start_assignment_phase(proposal)

    return review


def start_supervisor_phase(proposal):
    """
    Starts the supervisor phase:
    - Set the Review status to SUPERVISOR
    - Set date_submitted_supervisor to current date/time
    - Create a Decision for the supervisor
    - (TODO) Send an e-mail to the supervisor
    """
    review = Review.objects.create(proposal=proposal, date_start=timezone.now())
    review.stage = Review.SUPERVISOR
    review.save()

    proposal.date_submitted_supervisor = timezone.now()
    proposal.save()

    decision = Decision(review=review, reviewer=proposal.supervisor)
    decision.save()

    return review


def start_assignment_phase(proposal):
    """
    Starts the assignment phase:
    - Set the Review status to ASSIGNMENT
    - Set date_submitted to current date/time
    - Create a Decision for all Users in the 'Secretaris' Group
    - (TODO) Send an e-mail to these Users.
    """
    review = Review.objects.create(proposal=proposal, date_start=timezone.now())
    review.stage = Review.ASSIGNMENT
    review.save()

    proposal.date_submitted = timezone.now()
    proposal.save()

    for user in get_user_model().objects.filter(groups__name=SECRETARY):
        decision = Decision(review=review, reviewer=user)
        decision.save()

    return review


def auto_review(proposal):
    """
    Reviews a Proposal machine-wise. Based on the regulations on http://etcl.wp.hum.uu.nl/reglement/.
    """
    go = True
    reasons = []

    if proposal.study.legally_incapable:
        go = False
        reasons.append(_('De studie maakt gebruik van wilsonbekwame volwassenen.'))

    # TODO: is this correct?
    if proposal.study.has_traits:
        go = False
        reasons.append(_('De studie selecteert proefpersonen op bijzondere kenmerken die verhoogde kwetsbaarheid met zich meebrengen.'))

    for task in Task.objects.filter(session__proposal=proposal):
        for registration in task.registrations.all():
            if registration.requires_review:
                for age_group in proposal.study.age_groups.all():
                    if age_group.age_max < 18:
                        go = False
                        reasons.append(_('De studie gebruikt psychofysiologische metingen bij kinderen onder de 18 jaar.'))

    for recruitment in proposal.study.recruitment.all():
        if recruitment.requires_review:
            go = False
            reasons.append(_('De proefpersonen worden op een niet-standaard manier geworven.'))

    for session in proposal.session_set.all():
        if session.deception:
            go = False
            reasons.append(_('De studie maakt gebruik van misleiding.'))

    if proposal.session_set.count() > 1:
        go = False
        reasons.append(_('De studie bevat meerdere sessies, d.w.z. de proefpersoon neemt op meerdere dagen deel.'))

    # TODO: is this correct?
    if proposal.study.compensation.requires_review:
        go = False
        reasons.append(_('De beloning van proefpersonen wijkt af van de UiL OTS standaardregeling.'))

    if proposal.sessions_stressful or proposal.sessions_stressful is None:
        go = False
        reasons.append(_('Een onderdeel van de procedure kan belastend worden ervaren.'))

    if proposal.study.risk_physical or proposal.study.risk_psychological:
        go = False
        reasons.append(_('Er is een verhoogd risico op fysieke of psychische schade.'))

    for age_group in proposal.study.age_groups.all():
        if proposal.net_duration() > age_group.max_net_duration:
            go = False
            reasons.append(_('De procedure overschrijdt maximale duur voor leeftijdsgroep {}; totale nettoduur is {} minuten, streefmaximum voor deze leeftijdsgroep is {} minuten.'.format(age_group, proposal.net_duration(), age_group.max_net_duration)))

    return go, reasons
