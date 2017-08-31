# -*- encoding: utf-8 -*-

from django.conf import settings
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _
from django.utils import timezone

from core.models import YES, DOUBT
from core.utils import get_secretary
from tasks.models import Task
from proposals.utils import notify_local_staff
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
    - Send an e-mail to the creator
    - Send an e-mail to the supervisor
    """
    review = Review.objects.create(proposal=proposal, date_start=timezone.now())
    review.stage = Review.SUPERVISOR
    review.save()

    proposal.date_submitted_supervisor = timezone.now()
    proposal.status = proposal.SUBMITTED_TO_SUPERVISOR
    proposal.save()

    decision = Decision.objects.create(review=review, reviewer=proposal.supervisor)

    subject = _('ETCL: bevestiging indienen concept-aanmelding')
    params = {
        'supervisor': proposal.supervisor.get_full_name(),
        'secretary': get_secretary().get_full_name(),
    }
    msg_plain = render_to_string('mail/concept_creator.txt', params)
    send_mail(subject, msg_plain, settings.EMAIL_FROM, [proposal.created_by.email])

    subject = _('ETCL: beoordelen als eindverantwoordelijke')
    params = {
        'creator': proposal.created_by.get_full_name(),
        'proposal_url': settings.BASE_URL + reverse('reviews:decide', args=(decision.pk,)),
        'secretary': get_secretary().get_full_name(),
        'revision': proposal.is_revision,
        'revision_type': proposal.type(),
    }
    msg_plain = render_to_string('mail/concept_supervisor.txt', params)
    msg_html = render_to_string('mail/concept_supervisor.html', params)
    send_mail(subject, msg_plain, settings.EMAIL_FROM, [proposal.supervisor.email], html_message=msg_html)

    return review


def start_assignment_phase(proposal):
    """
    Starts the assignment phase:
    - Set the Review status to ASSIGNMENT
    - Do an automatic review to determine whether this Review can follow the short route
    - Set date_submitted on Proposal to current date/time
    - Create a Decision for all Users in the 'Secretaris' Group
    - Send an e-mail to these Users
    - Send an e-mail to the creator and supervisor
    - Send an e-mail to the local staff
    :param proposal: the current Proposal
    """
    reasons = auto_review(proposal)
    short_route = len(reasons) == 0

    review = Review.objects.create(proposal=proposal, date_start=timezone.now())
    review.stage = Review.ASSIGNMENT
    review.short_route = short_route
    if short_route:
        review.date_should_end = timezone.now() + timezone.timedelta(weeks=settings.SHORT_ROUTE_WEEKS)
    review.save()

    proposal.date_submitted = timezone.now()
    proposal.status = proposal.SUBMITTED
    proposal.save()

    secretary = get_secretary()
    Decision.objects.create(review=review, reviewer=secretary)

    notify_secretary_assignment(review)

    subject = _('ETCL: aanmelding ontvangen')
    params = {
        'secretary': secretary.get_full_name(),
        'review_date': review.date_should_end,
    }
    if review.short_route:
        msg_plain = render_to_string('mail/submitted_shortroute.txt', params)
        msg_html = render_to_string('mail/submitted_shortroute.html', params)
    else:
        msg_plain = render_to_string('mail/submitted_longroute.txt', params)
        msg_html = render_to_string('mail/submitted_longroute.html', params)
    recipients = [proposal.created_by.email]
    if proposal.relation.needs_supervisor:
        recipients.append(proposal.supervisor.email)
    send_mail(subject, msg_plain, settings.EMAIL_FROM, recipients, html_message=msg_html)

    if proposal.inform_local_staff:
        notify_local_staff(proposal)

    return review


def start_review_pre_assessment(proposal):
    """
    Starts the preliminary assessment Review:
    - Set the Review status to ASSIGNMENT
    - Set date_submitted on Proposal to current date/time
    - Create a Decision for all Users in the 'Secretaris' Group
    - Send an e-mail to these Users
    - Send an e-mail to the creator
    :param proposal: the current Proposal
    """
    review = Review.objects.create(proposal=proposal, date_start=timezone.now())
    review.stage = Review.ASSIGNMENT
    review.short_route = True
    review.date_should_end = timezone.now() + timezone.timedelta(weeks=settings.PREASSESSMENT_ROUTE_WEEKS)
    review.save()

    proposal.date_submitted = timezone.now()
    proposal.status = proposal.SUBMITTED
    proposal.save()

    secretary = get_secretary()
    Decision.objects.create(review=review, reviewer=secretary)

    subject = _('ETCL: nieuwe aanvraag voor voortoetsing')
    params = {
        'secretary': secretary.get_full_name(),
        'proposal': proposal,
        'proposal_pdf': settings.BASE_URL + proposal.pdf.url,
    }
    msg_plain = render_to_string('mail/pre_assessment_secretary.txt', params)
    msg_html = render_to_string('mail/pre_assessment_secretary.html', params)
    send_mail(subject, msg_plain, settings.EMAIL_FROM, [secretary.email], html_message=msg_html)

    subject = _('ETCL: bevestiging indienen aanvraag voor voortoetsing')
    params = {
        'secretary': secretary.get_full_name(),
    }
    msg_plain = render_to_string('mail/pre_assessment_creator.txt', params)
    send_mail(subject, msg_plain, settings.EMAIL_FROM, [proposal.created_by.email])


def start_review_route(review, commission_users, use_short_route):
    """
    Creates Decisions and sends notification e-mail to the selected Reviewers
    """
    for user in commission_users:
        Decision.objects.create(review=review, reviewer=user)

        template = 'mail/assignment_shortroute.txt' if use_short_route else 'mail/assignment_longroute.txt'
        subject = _('ETCL: nieuwe studie ter beoordeling')
        params = {
            'secretary': get_secretary().get_full_name(),
            'reviewer': user.get_full_name(),
            'review_date': review.date_should_end,
            'is_pre_assessment': review.proposal.is_pre_assessment,
        }
        msg_plain = render_to_string(template, params)
        send_mail(subject, msg_plain, settings.EMAIL_FROM, [user.email])


def notify_secretary_assignment(review):
    """
    Notifies the secretary a Proposal is ready for assigment
    """
    secretary = get_secretary()
    subject = _('ETCL: nieuwe studie ingediend')
    params = {
        'secretary': secretary.get_full_name(),
        'review': review,
    }
    msg_plain = render_to_string('mail/submitted.txt', params)
    send_mail(subject, msg_plain, settings.EMAIL_FROM, [secretary.email])


def notify_secretary(decision):
    """
    Notifies a secretary a Decision has been made by one of the members in the Commission
    """
    secretary = get_secretary()
    subject = _('ETCL: nieuwe beoordeling toegevoegd')
    params = {
        'secretary': secretary.get_full_name(),
        'decision': decision,
    }
    msg_plain = render_to_string('mail/decision_notify.txt', params)
    send_mail(subject, msg_plain, settings.EMAIL_FROM, [secretary.email])


def auto_review(proposal):
    """
    Reviews a Proposal machine-wise.
    Based on the regulations on http://etcl.wp.hum.uu.nl/reglement/.
    """
    reasons = []

    for study in proposal.study_set.all():
        if study.has_intervention:
            reasons.append(_('De studie is een interventiestudie.'))

        if study.legally_incapable:
            reasons.append(_('De studie maakt gebruik van wilsonbekwame volwassenen.'))

        if study.passive_consent:
            reasons.append(_('De studie werkt met passieve informed consent.'))

        if study.has_observation:
            reasons.extend(auto_review_observation(study.observation))

        if study.deception in [YES, DOUBT]:
            reasons.append(_('De studie maakt gebruik van misleiding.'))

        if study.compensation.requires_review:
            reasons.append(_('De beloning van deelnemers wijkt af van de UiL OTS standaardregeling.'))

        if study.has_traits:
            reasons.append(_('De studie selecteert deelnemers op bijzondere kenmerken die wellicht verhoogde kwetsbaarheid met zich meebrengen.'))

        for task in Task.objects.filter(session__study=study):
            reasons.extend(auto_review_task(study, task))

        if study.sessions_number > 1:
            reasons.append(_('De studie bevat meerdere sessies, d.w.z. de deelnemer neemt op meerdere dagen deel (zoals bij longitudinaal onderzoek).'))

        if study.stressful in [YES, DOUBT]:
            reasons.append(_('De onderzoeker geeft aan dat (of twijfelt erover of) de studie op onderdelen of \
als geheel zodanig belastend is dat deze ondanks de verkregen informed consent vragen zou kunnen oproepen.'))

        if study.risk in [YES, DOUBT]:
            reasons.append(_('De onderzoeker geeft aan dat (of twijfelt erover of) de risico\'s op psychische of \
fysieke schade bij deelname aan de studie meer dan minimaal zijn.'))

        if study.has_sessions:
            for session in study.session_set.all():
                for age_group in study.age_groups.all():
                    if session.net_duration() > age_group.max_net_duration:
                        reasons.append(_('De totale duur van de taken in sessie {s}, exclusief pauzes \
en andere niet-taak elementen ({d} minuten), is groter dan het streefmaximum ({max_d} minuten) \
voor de leeftijdsgroep {ag}.').format(s=session.order, ag=age_group, d=session.net_duration(), max_d=age_group.max_net_duration))

    return reasons


def auto_review_observation(observation):
    """
    Reviews an Observation machine-wise.
    Based on the regulations on http://etcl.wp.hum.uu.nl/reglement/.
    """
    reasons = []

    if observation.is_nonpublic_space:
        if not observation.has_advanced_consent:
            reasons.append(_('De studie observeert deelnemers in een niet-publieke ruimte en werkt met informed consent achteraf.'))
        if observation.is_anonymous:
            reasons.append(_('De onderzoeker begeeft zich "under cover" in een beheerde niet-publieke ruimte (bijv. een digitale gespreksgroep), en neemt actief aan de discussie deel en/of verzamelt data die te herleiden zijn tot individuele personen.'))

    return reasons


def auto_review_task(study, task):
    """
    Reviews a Task machine-wise.
    Based on the regulations on http://etcl.wp.hum.uu.nl/reglement/.
    """
    reasons = []

    for registration in task.registrations.all():
        if registration.requires_review:
            if registration.age_min:
                for age_group in study.age_groups.all():
                    if age_group.age_max is not None and age_group.age_max < registration.age_min:
                        reasons.append(_('De studie gebruikt psychofysiologische metingen bij kinderen onder de {} jaar.').format(registration.age_min))
                        break

    for registration_kind in task.registration_kinds.all():
        if registration_kind.requires_review:
            reasons.append(_('De studie maakt gebruik van {}').format(registration_kind.description))

    return reasons
