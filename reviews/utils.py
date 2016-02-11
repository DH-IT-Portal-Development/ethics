from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
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
    - Send an e-mail to the supervisor
    """
    review = Review.objects.create(proposal=proposal, date_start=timezone.now())
    review.stage = Review.SUPERVISOR
    review.save()

    proposal.date_submitted_supervisor = timezone.now()
    proposal.save()

    decision = Decision(review=review, reviewer=proposal.supervisor)
    decision.save()

    subject = 'ETCL: beoordelen als eindverantwoordelijke'
    message = 'Zie hier'
    send_mail(subject, message, settings.EMAIL_FROM, [proposal.supervisor.email])

    return review


def start_assignment_phase(proposal):
    """
    Starts the assignment phase:
    - Set the Review status to ASSIGNMENT
    - Set date_submitted to current date/time
    - Create a Decision for all Users in the 'Secretaris' Group
    - Send an e-mail to these Users.
    """
    review = Review.objects.create(proposal=proposal, date_start=timezone.now())
    review.stage = Review.ASSIGNMENT
    review.save()

    proposal.date_submitted = timezone.now()
    proposal.save()

    emails = []
    for user in get_user_model().objects.filter(groups__name=SECRETARY):
        decision = Decision(review=review, reviewer=user)
        decision.save()
        emails.append(user.email)

    subject = 'ETCL: aanstellen commissieleden'
    message = 'Zie hier'
    send_mail(subject, message, settings.EMAIL_FROM, emails)

    return review


def auto_review(proposal):
    """
    Reviews a Proposal machine-wise. Based on the regulations on http://etcl.wp.hum.uu.nl/reglement/.
    """
    study = proposal.study

    go = True
    reasons = []

    if study.legally_incapable:
        go = False
        reasons.append(_('De studie maakt gebruik van wilsonbekwame volwassenen.'))

    if study.has_traits:
        go = False
        reasons.append(_('De studie selecteert deelnemers op bijzondere kenmerken die verhoogde kwetsbaarheid met zich meebrengen.'))

    for task in Task.objects.filter(session__study=study):
        for registration in task.registrations.all():
            if registration.requires_review:
                if registration.age_min:
                    for age_group in study.age_groups.all():
                        if age_group.age_max < registration.age_min:
                            go = False
                            reasons.append(_('De studie gebruikt psychofysiologische metingen bij kinderen onder de {} jaar.'.format(registration.age_min)))
                            break
                else:
                    go = False
                    reasons.append(_('De studie gebruikt een afwijkende soort vastlegging van gegevens.'))

    for recruitment in study.recruitment.all():
        if recruitment.requires_review:
            go = False
            reasons.append(_('De deelnemers worden op een niet-standaard manier geworven.'))

    for session in study.session_set.all():
        if session.deception:
            go = False
            reasons.append(_('De studie maakt gebruik van misleiding.'))

    if study.session_set.count() > 1:
        go = False
        reasons.append(_('De studie bevat meerdere sessies, d.w.z. de deelnemer neemt op meerdere dagen deel.'))

    # TODO: is this correct?
    if study.compensation.requires_review:
        go = False
        reasons.append(_('De beloning van deelnemers wijkt af van de UiL OTS standaardregeling.'))

    if study.stressful:
        go = False
        reasons.append(_('Een onderdeel van de procedure kan belastend worden ervaren.'))

    if study.risk:
        go = False
        reasons.append(_('Er is een verhoogd risico op fysieke of psychische schade.'))

    for age_group in study.age_groups.all():
        if study.net_duration() > age_group.max_net_duration:
            go = False
            reasons.append(_('De procedure overschrijdt maximale duur voor leeftijdsgroep {}; totale nettoduur is {} minuten, streefmaximum voor deze leeftijdsgroep is {} minuten.'.format(age_group, study.net_duration(), age_group.max_net_duration)))

    return go, reasons
