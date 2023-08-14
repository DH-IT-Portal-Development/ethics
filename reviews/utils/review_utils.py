# -*- encoding: utf-8 -*-
import datetime

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
from ..models import Review, Decision


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
    reference = proposal.committee_prefixed_refnum()

    subject = _('FETC-GW {}: bevestiging indienen concept-aanmelding'.format(reference))
    params = {
        'proposal': proposal,
        'supervisor': proposal.supervisor.get_full_name(),
        'secretary': get_secretary().get_full_name(),
        'pdf_url': settings.BASE_URL + proposal.pdf.url,
    }
    msg_plain = render_to_string('mail/concept_creator.txt', params)
    msg_html = render_to_string('mail/concept_creator.html', params)
    send_mail(subject, msg_plain, settings.EMAIL_FROM, [proposal.created_by.email], html_message=msg_html)

    subject = _('FETC-GW {}: beoordelen als eindverantwoordelijke'.format(reference))
    params = {
        'proposal': proposal,
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

    subject = _('FETC-GW {}: aanmelding ontvangen'.format(proposal.committee_prefixed_refnum()))
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
        review__date_should_end__lte=next_two_days,
        go='',  # Checks if the decision has already been done; we don't
        # check for None as the field cannot be None according to the field
        # definition
    )

    for decision in decisions:
        proposal = decision.review.proposal
        subject = "Herinnering: beoordeel aanvraag {}".format(
            proposal.committee_prefixed_refnum(),
        )
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

    subject = _('FETC-GW {}: nieuwe aanvraag voor voortoetsing'.format(
        proposal.committee_prefixed_refnum(),
        )
                )
                
    params = {
        'secretary': secretary.get_full_name(),
        'proposal': proposal,
        'proposal_pdf': settings.BASE_URL + proposal.pdf.url,
    }
    msg_plain = render_to_string('mail/pre_assessment_secretary.txt', params)
    msg_html = render_to_string('mail/pre_assessment_secretary.html', params)
    send_mail(subject, msg_plain, settings.EMAIL_FROM, [secretary.email], html_message=msg_html)

    subject = _('FETC-GW {}: bevestiging indienen aanvraag voor voortoetsing'.format(
        proposal.committee_prefixed_refnum(),)
                )
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
        subject = 'FETC-GW {}: gereviseerde aanvraag ter beoordeling'
    else:
        subject = 'FETC-GW {}: nieuwe aanvraag ter beoordeling'
        # These emails are Dutch-only, therefore intentionally untranslated

    subject = subject.format(review.proposal.committee_prefixed_refnum(),
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
    subject = _('FETC-GW {}: nieuwe aanvraag ingediend').format(proposal.committee_prefixed_refnum())
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
    subject = _('FETC-GW {}: nieuwe beoordeling toegevoegd').format(
        proposal.committee_prefixed_refnum(),
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
    subject = _('FETC-GW {}: eindverantwoordelijke heeft je aanvraag beoordeeld'.format(
        proposal.committee_prefixed_refnum(),)
    )
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
    https://fetc-gw.wp.hum.uu.nl/reglement-fetc-gw/.
    """
    reasons = []

    for study in proposal.study_set.all():

        if study.legally_incapable:
            reasons.append(_('De aanvraag bevat het gebruik van wilsonbekwame volwassenen.'))

        if study.deception in [YES, DOUBT]:
            reasons.append(_('De aanvraag bevat het gebruik van misleiding.'))

        if study.hierarchy:
            reasons.append(_('Er bestaat een hiërarchische relatie tussen de onderzoeker(s) en deelnemer(s)'))

        if study.has_special_details:
            reasons.append(_('Het onderzoek verzamelt bijzondere persoonsgegevens.'))

        if study.has_traits:
            reasons.append(_('Het onderzoek selecteert deelnemers op bijzondere kenmerken die wellicht verhoogde kwetsbaarheid met zich meebrengen.'))

        for task in Task.objects.filter(session__study=study):
            reasons.extend(auto_review_task(study, task))

        if study.stressful in [YES, DOUBT]:
            reasons.append(_('De onderzoeker geeft aan dat (of twijfelt erover of) het onderzoek op onderdelen of \
als geheel zodanig belastend is dat deze ondanks de verkregen informed consent vragen zou kunnen oproepen.'))

        if study.risk in [YES, DOUBT]:
            reasons.append(_('De onderzoeker geeft aan dat (of twijfelt erover of) de risico\'s op psychische of \
fysieke schade bij deelname aan het onderzoek meer dan minimaal zijn.'))

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
    Based on the regulations on
    https://fetc-gw.wp.hum.uu.nl/reglement-fetc-gw/.
    """
    reasons = []

    if observation.settings_requires_review():
        for setting in observation.settings_requires_review():
            reasons.append(_('Het onderzoek observeert deelnemers in de volgende setting: {s}').format(s=setting))

    if observation.is_nonpublic_space:
        if not observation.has_advanced_consent:
            reasons.append(_('Het onderzoek observeert deelnemers in een niet-publieke ruimte en werkt met informed consent achteraf.'))
        if observation.is_anonymous:
            reasons.append(_('De onderzoeker begeeft zich "under cover" in een beheerde niet-publieke ruimte (bijv. een digitale gespreksgroep), en neemt actief aan de discussie deel en/of verzamelt data die te herleiden zijn tot individuele personen.'))

    for registration in observation.registrations.all():
        if registration.requires_review:
            reasons.append(
                _('De aanvraag bevat het gebruik van {}').format(
                    registration.description
                )
            )

    return reasons


def auto_review_task(study, task):
    """
    Reviews a Task machine-wise.
    Based on the regulations on
    https://fetc-gw.wp.hum.uu.nl/reglement-fetc-gw/.
    """
    reasons = []

    for registration in task.registrations.all():
        if registration.requires_review:
            if registration.age_min:
                for age_group in study.age_groups.all():
                    if age_group.age_max is not None and age_group.age_max < registration.age_min:
                        reasons.append(_('De aanvraag bevat psychofysiologische metingen bij kinderen onder de {} jaar.').format(registration.age_min))
                        break

    return reasons


def discontinue_review(review):
    """
    Set continuation to discontinued on the given review,
    and set DECISION_MADE on its proposal. """

    # Set review continuation
    review.continuation = review.DISCONTINUED
    review.proposal.status = review.proposal.DECISION_MADE
    review.stage = review.CLOSED
    review.date_end = datetime.datetime.now()
    review.save()
    review.proposal.save()


def assign_reviewers(review, list_of_users, route):
    """Assigns or reassigns a list of reviewers to a review"""

    # Set stage to commission if users are assigned
    if len(list_of_users) > 0:
        review.stage = review.COMMISSION
    else:
        review.stage = review.ASSIGNMENT

    current_reviewers = set(review.current_reviewers())
    new_reviewers = list_of_users - current_reviewers
    obsolete_reviewers = current_reviewers - list_of_users

    # Set the proper end date
    # It should be 2 weeks for short_routes
    if review.short_route and review.date_should_end is None:
        review.date_should_end = timezone.now() + \
            timezone.timedelta(
                weeks=settings.SHORT_ROUTE_WEEKS
            )
    elif review.proposal.is_revision and review.date_should_end is None:
        #It seems desiree wants the should end date to be within one week
        #if a proposal is a revision
        #TODO: discuss with Ty
        review.date_should_end = timezone.now() + \
            timezone.timedelta(
                weeks=1
            )
    elif review.date_should_end is not None:
        # We have no desired end date for long track reviews
        review.date_should_end = None

    # Create a new Decision for new reviewers
    start_review_route(review, new_reviewers, route)

    # Remove the Decision for obsolete reviewers
    Decision.objects.filter(review=review,
                            reviewer__in=obsolete_reviewers).delete()

    review.save()

    # Finally, update the review process
    # This prevents it waiting for removed reviewers
    review.update_go()

def straight_to_revision(review):
    """This action by the secretary in ReviewAssignForm bypasses
    the usual review process and sends a review straight to revision"""
