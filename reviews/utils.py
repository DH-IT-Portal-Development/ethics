# -*- encoding: utf-8 -*-

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _
from django.utils import timezone

from core.models import YES, DOUBT
from core.utils import get_secretary
from observations.models import Observation
from tasks.models import Task
from .models import Review, Decision


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
    - Send an e-mail to the creator
    """
    review = Review.objects.create(proposal=proposal, date_start=timezone.now())
    review.stage = Review.SUPERVISOR
    review.save()

    proposal.date_submitted_supervisor = timezone.now()
    proposal.save()

    decision = Decision(review=review, reviewer=proposal.supervisor)
    decision.save()

    subject = _('ETCL: bevestiging indienen concept-aanmelding')
    params = {'secretary': get_secretary().get_full_name()}
    msg_plain = render_to_string('mail/concept_creator.txt', params)
    send_mail(subject, msg_plain, settings.EMAIL_FROM, [proposal.created_by.email])

    subject = _('ETCL: beoordelen als eindverantwoordelijke')
    params = {'creator': proposal.created_by, 'proposal_url': 'test', 'secretary': get_secretary().get_full_name()}
    msg_plain = render_to_string('mail/concept_supervisor.txt', params)
    send_mail(subject, msg_plain, settings.EMAIL_FROM, [proposal.supervisor.email])

    return review


def start_assignment_phase(proposal):
    """
    Starts the assignment phase:
    - Set the Review status to ASSIGNMENT
    - Do an automatic review to determine whether this Review can follow the short route
    - Set date_submitted on Proposal to current date/time
    - Create a Decision for all Users in the 'Secretaris' Group
    - Send an e-mail to these Users
    - Send an e-mail to the supervisor
    """
    secretary = get_secretary()
    auto_go = auto_review(proposal)[0]
    review = Review.objects.create(proposal=proposal, date_start=timezone.now())
    review.stage = Review.ASSIGNMENT
    review.short_route = auto_go
    review.save()

    proposal.date_submitted = timezone.now()
    proposal.save()

    decision = Decision(review=review, reviewer=secretary)
    decision.save()

    subject = _('ETCL: nieuwe studie ingediend')
    params = {'review': review, 'secretary': secretary.get_full_name()}
    msg_plain = render_to_string('mail/submitted.txt', params)
    send_mail(subject, msg_plain, settings.EMAIL_FROM, [secretary.email])

    responsible = proposal.supervisor if proposal.relation.needs_supervisor else proposal.created_by

    subject = _('ETCL: aanmelding ontvangen')
    params = {'review': review, 'secretary': secretary.get_full_name()}
    if review.short_route:
        msg_plain = render_to_string('mail/submitted_shortroute.txt', params)
    else:
        msg_plain = render_to_string('mail/submitted_longroute.txt', params)
    send_mail(subject, msg_plain, settings.EMAIL_FROM, [responsible.email])

    return review


def auto_review(proposal):
    """
    Reviews a Proposal machine-wise. Based on the regulations on http://etcl.wp.hum.uu.nl/reglement/.
    """
    go = True
    reasons = []

    for funding in proposal.funding.all():
        if funding.requires_review:
            go = False
            reasons.append(_('De studie heeft een afwijkende geldstroom.'))
            break

    for study in proposal.study_set.all():
        if study.legally_incapable:
            go = False
            reasons.append(_('De studie maakt gebruik van wilsonbekwame volwassenen.'))

        if study.passive_consent:
            go = False
            reasons.append(_('De studie werkt met passieve informed consent.'))

        # TODO: is this correct?
        for session in study.session_set.all():
            for setting in session.setting.all():
                if setting.requires_review:
                    go = False
                    reasons.append(_('De dataverzameling vindt op een afwijkende plek plaats.'))
                    break

        if study.deception in [YES, DOUBT]:
            go = False
            reasons.append(_('De studie maakt gebruik van misleiding.'))
            break

        # TODO: is this correct?
        if study.compensation.requires_review:
            go = False
            reasons.append(_('De beloning van deelnemers wijkt af van de UiL OTS standaardregeling.'))

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
                        # TODO: not necessary?
                        go = False
                        reasons.append(_('De studie gebruikt een afwijkende soort vastlegging van gegevens.'))
                        break
            for registration_kind in task.registration_kinds.all():
                if registration_kind.requires_review:
                    go = False
                    reasons.append(_('De studie maakt gebruik van {}'.format(registration_kind.description)))

        # TODO: not necessary?
        for recruitment in study.recruitment.all():
            if recruitment.requires_review:
                go = False
                reasons.append(_('De deelnemers worden op een niet-standaard manier geworven.'))
                break

        if study.stressful in [YES, DOUBT]:
            go = False
            reasons.append(_('De onderzoeker geeft aan dat (of twijfelt erover of) de studie op onderdelen of \
als geheel zodanig belastend is dat deze ondanks de verkregen informed consent vragen zou kunnen oproepen.'))

        if study.risk in [YES, DOUBT]:
            go = False
            reasons.append(_('De onderzoeker geeft aan dat (of twijfelt erover of) de risico\'s op psychische of \
fysieke schade bij deelname aan de studie meer dan minimaal zijn.'))

        for age_group in study.age_groups.all():
            if study.net_duration() > age_group.max_net_duration:
                go = False
                reasons.append(_('De totale duur van de taken in de sessie ({d} minuten), exclusief pauzes \
en andere niet-taak elementen, is groter dan het streefmaximum ({max_d} minuten) \
voor de leeftijdsgroep {ag}.'.format(ag=age_group, d=study.net_duration(), max_d=age_group.max_net_duration)))

        if study.has_observation:
            observation = Observation.objects.get(study=study)
            if observation.is_anonymous:
                go = False
                reasons.append(_('De observatie gebeurt anoniem.'))

    return go, reasons
