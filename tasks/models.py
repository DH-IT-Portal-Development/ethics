from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _

from main.models import SettingModel
from studies.models import Study


class Session(SettingModel):
    order = models.PositiveIntegerField()

    # Fields with respect to Tasks
    tasks_number = models.PositiveIntegerField(
        _('Hoeveel taken worden er binnen deze sessie bij de deelnemer afgenomen?'),
        null=True,
        validators=[MinValueValidator(1), MaxValueValidator(100)], # Max of 100 is a technical safeguard
        help_text=_('Wanneer je bijvoorbeeld eerst de deelnemer observeert \
en de deelnemer vervolgens een vragenlijst afneemt, dan vul je hierboven "2" '
                    'in. Electrodes plakken, sessie-debriefing en kort '
                    '(< 3 minuten) exit-interview gelden niet als een taak.')
    )

    tasks_duration = models.PositiveIntegerField(
        _('De totale geschatte netto taakduur van je sessie komt \
op basis van je opgave per taak uit op <strong>%d minuten</strong>. \
Hoe lang duurt <em>de totale sessie</em>, inclusief ontvangst, \
instructies per taak, pauzes tussen taken, en debriefing? \
(bij labbezoek dus van binnenkomst tot vertrek)'),
        null=True,
        blank=True,
    )

    # References
    study = models.ForeignKey(Study, on_delete=models.CASCADE)

    class Meta:
        ordering = ['order']
        unique_together = ('study', 'order')

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
        Returns the current (incomplete) Task.
        - If all Tasks are completed, the last Task is returned.
        - If no Tasks have yet been created, None is returned.
        """
        current_task = None
        for task in self.task_set.all():
            current_task = task
            if not task.is_completed():
                break
        return current_task

    def tasks_completed(self):
        result = True
        if self.task_set.count() == 0:
            result = False
        for task in self.task_set.all():
            result &= task.is_completed()
        return result

    def is_completed(self):
        result = self.tasks_completed()
        result &= self.tasks_duration is not None
        return result

    def __str__(self):
        return _('Sessie {}').format(self.order)


class Registration(models.Model):
    order = models.PositiveIntegerField(unique=True)
    description = models.CharField(max_length=200)
    is_local = models.BooleanField(default=False)
    needs_details = models.BooleanField(default=False)
    needs_kind = models.BooleanField(default=False)
    requires_review = models.BooleanField(default=False)
    age_min = models.PositiveIntegerField(blank=True, null=True)

    class Meta:
        ordering = ['order']
        verbose_name = _('Vastlegging gedrag')

    def __str__(self):
        return self.description


class RegistrationKind(models.Model):
    order = models.PositiveIntegerField(unique=True)
    description = models.CharField(max_length=200)
    needs_details = models.BooleanField(default=False)
    requires_review = models.BooleanField(default=False)
    registration = models.ForeignKey(Registration, on_delete=models.CASCADE)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.description


class Task(models.Model):
    order = models.PositiveIntegerField()
    name = models.CharField(
        _('Wat is de naam van de taak?'),
        max_length=200,
        blank=True,
    )

    description = models.TextField(
        _('Beschrijf de taak die de deelnemer moet uitvoeren, en leg kort \
uit hoe deze taak (en de eventuele manipulaties daarbinnen) aan de \
beantwoording van jouw onderzoeksvragen bijdraagt. \
Geef, kort, een paar voorbeelden (of beschrijvingen) van het type stimuli \
dat je van plan bent aan de deelnemer aan te bieden. \
Het moet voor de commissieleden duidelijk zijn wat je precies gaat doen.'),
        blank=True,
    )

    duration = models.PositiveIntegerField(
        _('Wat is de duur van deze taak van begin tot eind in <strong>minuten</strong>, \
dus vanaf het moment dat de taak van start gaat tot en met het einde van de taak \
(exclusief instructie maar inclusief oefensessie)? \
Indien de taakduur per deelnemer varieert (self-paced taak of task-to-criterion), \
geef dan <strong>het redelijkerwijs te verwachten maximum op</strong>.'),
        default=0,
        validators=[MinValueValidator(1)],
        blank=True,
    )

    registrations = models.ManyToManyField(
        Registration,
        verbose_name=_('Hoe wordt het gedrag of de toestand van de deelnemer bij deze taak vastgelegd?')
    )

    registrations_details = models.CharField(
        _('Namelijk'),
        max_length=200,
        blank=True,
    )

    registration_kinds = models.ManyToManyField(
        RegistrationKind,
        verbose_name=_('Kies het soort meting'),
        blank=True,
    )

    registration_kinds_details = models.CharField(
        _('Namelijk'),
        max_length=200,
        blank=True,
    )

    feedback = models.BooleanField(
        _('Krijgt de deelnemer tijdens of na deze taak feedback op hun '
          'gedrag of toestand?'),
        null=True,
        blank=True,
    )

    feedback_details = models.TextField(
        _('Beschrijf hoe de feedback wordt gegeven.'),
        blank=True,
    )

    # References
    session = models.ForeignKey(Session, on_delete=models.CASCADE)

    class Meta:
        ordering = ['order']
        unique_together = ('session', 'order')

    def is_completed(self):
        return self.name != ''

    def delete(self, *args, **kwargs):
        """
        Invalidate the totals on Session level on deletion of a Task.
        """
        session = self.session
        session.tasks_duration = None
        super(Task, self).delete(*args, **kwargs)
        session.save()

    def __str__(self):
        return _('Taak {} in sessie {}').format(self.order, self.session.order)
