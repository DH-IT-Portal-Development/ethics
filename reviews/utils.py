# -*- encoding: utf-8 -*-
from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from main.models import YES, DOUBT
from main.utils import get_secretary
from proposals.models import Proposal
from tasks.models import Task
from proposals.utils import notify_local_staff
from .models import Review, Decision

import datetime

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

    subject = _('FETC-GW: bevestiging indienen concept-aanmelding')
    params = {
        'supervisor': proposal.supervisor.get_full_name(),
        'secretary': get_secretary().get_full_name(),
        'pdf_url': settings.BASE_URL + proposal.pdf.url,
    }
    msg_plain = render_to_string('mail/concept_creator.txt', params)
    msg_html = render_to_string('mail/concept_creator.html', params)
    send_mail(subject, msg_plain, settings.EMAIL_FROM, [proposal.created_by.email], html_message=msg_html)

    subject = _('FETC-GW: beoordelen als eindverantwoordelijke')
    params = {
        'creator': proposal.created_by.get_full_name(),
        'proposal_url': settings.BASE_URL + reverse('reviews:decide', args=(decision.pk,)),
        'secretary': get_secretary().get_full_name(),
        'revision': proposal.is_revision,
        'revision_type': proposal.type(),
        'my_supervised': settings.BASE_URL + reverse('proposals:my_supervised'),
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

    subject = _('FETC-GW: aanmelding ontvangen')
    params = {
        'secretary': secretary.get_full_name(),
        'review_date': review.date_should_end,
        'pdf_url': settings.BASE_URL + proposal.pdf.url,
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


def remind_reviewers():
    """
    Sends an email to a reviewer to remind them to review a proposal.
    The reminders are only sent for proposals that are on the short track and need to be reviewed in the next 2 days
    """

    today = datetime.date.today()
    next_two_days = today + datetime.timedelta(days=2)

    decisions = Decision.objects.filter(
        review__stage=Review.COMMISSION,
        review__short_route=True,
        review__date_should_end__gte=today,
        review__date_should_end__lte=next_two_days
    )

    for decision in decisions:
        proposal = decision.review.proposal
        subject = 'FETC-GW: beoordelen studie (Herrinering)'
        params = {
            'creator': proposal.created_by.get_full_name(),
            'proposal_url': settings.BASE_URL + reverse('reviews:decide', args=(decision.pk,)),
            'secretary': get_secretary().get_full_name(),
        }
        msg_plain = render_to_string('mail/reminder.txt', params)
        msg_html = render_to_string('mail/reminder.html', params)
        send_mail(subject, msg_plain, settings.EMAIL_FROM, [decision.reviewer.email], html_message=msg_html)


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

    subject = _('FETC-GW: nieuwe aanvraag voor voortoetsing')
    params = {
        'secretary': secretary.get_full_name(),
        'proposal': proposal,
        'proposal_pdf': settings.BASE_URL + proposal.pdf.url,
    }
    msg_plain = render_to_string('mail/pre_assessment_secretary.txt', params)
    msg_html = render_to_string('mail/pre_assessment_secretary.html', params)
    send_mail(subject, msg_plain, settings.EMAIL_FROM, [secretary.email], html_message=msg_html)

    subject = _('FETC-GW: bevestiging indienen aanvraag voor voortoetsing')
    params = {
        'secretary': secretary.get_full_name(),
    }
    msg_plain = render_to_string('mail/pre_assessment_creator.txt', params)
    send_mail(subject, msg_plain, settings.EMAIL_FROM, [proposal.created_by.email])


def start_review_route(review, commission_users, use_short_route):
    """
    Creates Decisions and sends notification e-mail to the selected Reviewers
    """
      
    template = 'mail/assignment_shortroute.txt' if use_short_route else 'mail/assignment_longroute.txt'
    
    was_revised = review.proposal.is_revision
    
    if was_revised:
        subject = 'FETC-GW {} {}: gereviseerde studie ter beoordeling'
    else:
        subject = 'FETC-GW {} {}: nieuwe studie ter beoordeling'
        # These emails are Dutch-only, therefore intentionally untranslated
    
    subject = subject.format(review.proposal.reviewing_committee,
                             review.proposal.reference_number,
                             )
    
    for user in commission_users:
        
        Decision.objects.create(review=review, reviewer=user)
        params = {
            'secretary': get_secretary().get_full_name(),
            'reviewer': user.get_full_name(),
            'review_date': review.date_should_end,
            'is_pre_assessment': review.proposal.is_pre_assessment,
            'was_revised': was_revised,
        }
        msg_plain = render_to_string(template, params)
        send_mail(subject, msg_plain, settings.EMAIL_FROM, [user.email])


def notify_secretary_assignment(review):
    """
    Notifies the secretary a Proposal is ready for assigment
    """
    secretary = get_secretary()
    proposal = review.proposal
    committee = review.proposal.reviewing_committee
    subject = _('FETC-GW {} {}: nieuwe studie ingediend').format(committee, proposal.reference_number)
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
    proposal = decision.review.proposal
    subject = _('FETC-GW {} {}: nieuwe beoordeling toegevoegd').format(
        proposal.reviewing_committee,
        proposal.reference_number,
        )
    params = {
        'secretary': secretary.get_full_name(),
        'decision': decision,
    }
    msg_plain = render_to_string('mail/decision_notify.txt', params)
    send_mail(subject, msg_plain, settings.EMAIL_FROM, [secretary.email])


def notify_supervisor_nogo(decision):
    secretary = get_secretary()
    proposal = decision.review.proposal
    supervisor = proposal.supervisor
    receivers = set(applicant for applicant in proposal.applicants.all())
    subject = _('FETC-GW: eindverantwoordelijke heeft uw studie beoordeeld')
    
    params = {
        'secretary': secretary.get_full_name(),
        'decision': decision,
        'supervisor': supervisor,
    }
    
    for applicant in receivers:
        params['applicant'] = applicant
        msg_plain = render_to_string('mail/supervisor_decision.txt', params)
        send_mail(subject, msg_plain, settings.EMAIL_FROM, [applicant.email])
    
    

def auto_review(proposal: Proposal):
    """
    Reviews a Proposal machine-wise.
    Based on the regulations on
    http://fetc-gw.wp.hum.uu.nl/reglement-algemene-kamer/.
    """
    reasons = []

    # Use the provided date_submitted if available, otherwise pretend it is
    # today
    # (It almost certainly is now, as it's only not set when called in the
    # submit method)
    if proposal.date_submitted:
        date_submitted = proposal.date_submitted.date()
    else:
        date_submitted = datetime.date.today()

    if proposal.date_start and proposal.date_start < date_submitted:
        reasons.append(_("De beoogde startdatum ligt voor de datum van "
                         "indiening"))

    for study in proposal.study_set.all():

        if study.has_intervention:
            reasons.append(_('De studie is een interventiestudie.'))

            for setting in study.intervention.settings_requires_review():
                reasons.append(
                    _('De studie heeft een interventiestudie met deelnemers in de volgende setting: {s}').format(s=setting))

        if study.legally_incapable:
            reasons.append(_('De studie maakt gebruik van wilsonbekwame volwassenen.'))

        if study.passive_consent:
            reasons.append(_('De studie werkt met passieve informed consent.'))

        if study.has_observation:
            reasons.extend(auto_review_observation(study.observation))

        if study.deception in [YES, DOUBT]:
            reasons.append(_('De studie maakt gebruik van misleiding.'))

        if study.compensation.requires_review:
            reasons.append(_('De beloning van deelnemers wijkt af van de '
                             'standaardregeling.'))

        if study.has_traits:
            reasons.append(_('De studie selecteert deelnemers op bijzondere kenmerken die wellicht verhoogde kwetsbaarheid met zich meebrengen.'))

        for task in Task.objects.filter(session__study=study):
            reasons.extend(auto_review_task(study, task))

        if study.sessions_number and study.sessions_number > 1:
            reasons.append(_('De studie bevat meerdere sessies, d.w.z. de deelnemer neemt op meerdere dagen deel (zoals bij longitudinaal onderzoek).'))

        if study.stressful in [YES, DOUBT]:
            reasons.append(_('De onderzoeker geeft aan dat (of twijfelt erover of) de studie op onderdelen of \
als geheel zodanig belastend is dat deze ondanks de verkregen informed consent vragen zou kunnen oproepen.'))

        if study.risk in [YES, DOUBT]:
            reasons.append(_('De onderzoeker geeft aan dat (of twijfelt erover of) de risico\'s op psychische of \
fysieke schade bij deelname aan de studie meer dan minimaal zijn.'))

        if study.has_sessions:
            for session in study.session_set.all():
                for setting in session.settings_requires_review():
                    reasons.append(
                        _('De studie heeft sessies met deelnemers in de volgende setting: {s}').format(s=setting))

                for age_group in study.age_groups.all():
                    if session.net_duration() > age_group.max_net_duration:
                        reasons.append(_('De totale duur van de taken in sessie {s}, exclusief pauzes \
en andere niet-taak elementen ({d} minuten), is groter dan het streefmaximum ({max_d} minuten) \
voor de leeftijdsgroep {ag}.').format(s=session.order, ag=age_group, d=session.net_duration(), max_d=age_group.max_net_duration))

    return reasons


def auto_review_observation(observation):
    """
    Reviews an Observation machine-wise.
    Based on the regulations on
    http://fetc-gw.wp.hum.uu.nl/reglement-algemene-kamer/.
    """
    reasons = []

    if observation.settings_requires_review():
        for setting in observation.settings_requires_review():
            reasons.append(_('De studie observeert deelnemers in de volgende setting: {s}').format(s=setting))

    if observation.is_nonpublic_space:
        if not observation.has_advanced_consent:
            reasons.append(_('De studie observeert deelnemers in een niet-publieke ruimte en werkt met informed consent achteraf.'))
        if observation.is_anonymous:
            reasons.append(_('De onderzoeker begeeft zich "under cover" in een beheerde niet-publieke ruimte (bijv. een digitale gespreksgroep), en neemt actief aan de discussie deel en/of verzamelt data die te herleiden zijn tot individuele personen.'))

    for registration in observation.registrations.all():
        if registration.requires_review:
            reasons.append(
                _('De studie maakt gebruik van {}').format(
                    registration.description
                )
            )

    return reasons


def auto_review_task(study, task):
    """
    Reviews a Task machine-wise.
    Based on the regulations on
    http://fetc-gw.wp.hum.uu.nl/reglement-algemene-kamer/.
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
