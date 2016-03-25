from django.db import models
from django.core.validators import MinValueValidator
from django.utils.translation import ugettext_lazy as _

from proposals.models import Study


class Session(models.Model):
    order = models.PositiveIntegerField()

    # Fields with respect to Tasks
    tasks_number = models.PositiveIntegerField(
        _('Hoeveel taken worden er binnen deze sessie bij de deelnemer afgenomen?'),
        null=True,
        validators=[MinValueValidator(1)],
        help_text=_('Wanneer u bijvoorbeeld eerst de deelnemer observeert \
en de deelnemer vervolgens een vragenlijst afneemt, dan vult u hierboven "2" in. \
Electrodes plakken, sessie-debriefing en kort (< 3 minuten) exit-interview gelden niet als een taak.'))
    tasks_duration = models.PositiveIntegerField(
        _('De totale geschatte netto taakduur van uw sessie komt \
op basis van uw opgave per taak uit op <strong>%d minuten</strong>. \
Hoe lang duurt <em>de totale sessie</em>, inclusief ontvangst, instructies per taak, \
pauzes tussen taken, en debriefing? (bij labbezoek dus van binnenkomst tot vertrek)'),
        null=True)

    # References
    study = models.ForeignKey(Study)

    class Meta:
        ordering = ['order']
        unique_together = ('study', 'order')

    def save(self, *args, **kwargs):
        """Sets the correct status on Proposal on save of a Session"""
        super(Session, self).save(*args, **kwargs)
        self.study.proposal.save()

    def delete(self, *args, **kwargs):
        """
        Invalidate the totals on Study level on deletion of a Session.
        """
        study = self.study
        study.sessions_duration = None
        super(Session, self).delete(*args, **kwargs)
        study.save()

    def net_duration(self):
        return self.task_set.aggregate(models.Sum('duration'))['duration__sum']

    def first_task(self):
        tasks = self.task_set.order_by('order')
        return tasks[0] if tasks else None

    def last_task(self):
        tasks = self.task_set.order_by('-order')
        return tasks[0] if tasks else None

    def current_task(self):
        """
        Returns the current (imcomplete) Task.
        - If all Tasks are completed, the last Task is returned.
        - If no Tasks have yet been created, None is returned.
        """
        current_task = None
        for task in self.task_set.all():
            current_task = task
            if not task.name:
                break
        return current_task

    def all_tasks_completed(self):
        result = True
        if self.task_set.count() == 0:
            result = False
        for task in self.task_set.all():
            result &= task.name != ''
        return result

    def __unicode__(self):
        return _('Sessie {}').format(self.order)


class Registration(models.Model):
    order = models.PositiveIntegerField(unique=True)
    description = models.CharField(max_length=200)
    needs_details = models.BooleanField(default=False)
    needs_kind = models.BooleanField(default=False)
    requires_review = models.BooleanField(default=False)
    age_min = models.PositiveIntegerField(blank=True, null=True)

    class Meta:
        ordering = ['order']

    def __unicode__(self):
        return self.description


class RegistrationKind(models.Model):
    order = models.PositiveIntegerField(unique=True)
    description = models.CharField(max_length=200)
    needs_details = models.BooleanField(default=False)
    requires_review = models.BooleanField(default=False)
    registration = models.ForeignKey(Registration)

    class Meta:
        ordering = ['order']

    def __unicode__(self):
        return self.description


class Task(models.Model):
    order = models.PositiveIntegerField()
    name = models.CharField(
        _('Wat is de naam van de taak?'),
        max_length=200)
    description = models.TextField(
        _('Wat is de beschrijving van de taak?'))
    duration = models.PositiveIntegerField(
        _('Wat is de duur van deze taak van begin tot eind in <strong>minuten</strong>, \
dus vanaf het moment dat de taak van start gaat tot en met het einde van de taak \
(exclusief instructie maar inclusief oefensessie)? \
Indien de taakduur per deelnemer varieert (self-paced taak of task-to-criterion), \
geef dan het redelijkerwijs te verwachten maximum op.'),
        default=0,
        validators=[MinValueValidator(1)])
    registrations = models.ManyToManyField(
        Registration,
        verbose_name=_('Hoe wordt het gedrag of de toestand van de deelnemer bij deze taak vastgelegd?'))
    registrations_details = models.CharField(
        _('Namelijk'),
        max_length=200,
        blank=True)
    registration_kinds = models.ManyToManyField(
        RegistrationKind,
        verbose_name=_('Kies het soort meting'),
        blank=True)
    registration_kinds_details = models.CharField(
        _('Namelijk'),
        max_length=200,
        blank=True)
    feedback = models.BooleanField(
        _('Krijgt de deelnemer tijdens of na deze taak feedback op zijn/haar gedrag of toestand?'),
        default=False)
    feedback_details = models.TextField(
        _('Beschrijf hoe de feedback wordt gegeven.'),
        blank=True)
    deception = models.BooleanField(
        _('Is er binnen deze sessie sprake van misleiding van de deelnemer, \
d.w.z. het doelbewust verschaffen van inaccurate informatie over het doel en/of \
belangrijke aspecten van de gang van zaken tijdens de studie? \
Denk aan zaken als een bewust misleidende "cover story" voor het experiment; \
het ten onrechte suggereren dat er met andere deelnemers wordt samengewerkt; \
het onaangekondigd aanbieden van een cruciale geheugentaak of het geven van gefingeerde feedback.'),
        help_text=_('Wellicht ten overvloede: het gaat hierbij niet om fillers.'),
        default=False)
    deception_details = models.TextField(
        _('Geef een toelichting en beschrijf hoe en wanneer de deelnemer zal worden gedebrieft.'),
        blank=True)

    # References
    session = models.ForeignKey(Session)

    class Meta:
        ordering = ['order']
        unique_together = ('session', 'order')

    def save(self, *args, **kwargs):
        """
        Sets the correct status on Proposal on save of a Task.
        """
        super(Task, self).save(*args, **kwargs)
        self.session.study.proposal.save()

    def delete(self, *args, **kwargs):
        """
        Invalidate the totals on Session/Study level on deletion of a Task.
        """
        session = self.session
        session.tasks_duration = None
        study = self.session.study
        study.sessions_duration = None
        super(Task, self).delete(*args, **kwargs)
        session.save()
        study.save()

    def __unicode__(self):
        return 'Task at {}'.format(self.session)
