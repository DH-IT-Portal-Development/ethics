from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _

from main.models import SettingModel


class Session(SettingModel):
    order = models.PositiveIntegerField()

    repeats = models.PositiveBigIntegerField(
        _("Hoe vaak wordt per deelnemer deze sessie uitgevoerd?"),
        help_text=_(
            "Het kan zijn dat een zelfde sessie meerdere keren moet worden \
                    uitgevoerd. Als dit het geval is, kun je dat hier \
                    aangeven. Als er variatie zit in de verschillende \
                    sessies van je onderzoek, maak dan een nieuwe sessie \
                    aan voor elke unieke sessie."
        ),
        null=False,
        default=1,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(100),
        ],  # Max of 100 is a technical safeguard
    )

    tasks_duration = models.PositiveIntegerField(
        _(
            "De totale geschatte netto taakduur van je sessie komt "
            "op basis van je opgave per taak uit op <strong>%d minuten</strong>. "
            "Hoeveel minuten duurt de totale sessie, inclusief ontvangst, "
            "instructies per taak, pauzes tussen taken, en debriefing? "
            "(bij labbezoek dus van binnenkomst tot vertrek en bij een "
            "focus-groep van ontvangst tot afsluiting)"
        ),
        null=True,
        blank=True,
    )

    # References
    study = models.ForeignKey("studies.Study", on_delete=models.CASCADE)

    class Meta:
        ordering = ["order"]
        unique_together = ("study", "order")

    def net_duration(self):
        if duration := self.task_set.annotate(
            total_duration=models.F("duration") * models.F("repeats")
        ).aggregate(models.Sum("total_duration"))["total_duration__sum"]:
            return duration

        return 0

    @property
    def tasks_number(self):
        return self.task_set.count()

    def first_task(self):
        tasks = self.task_set.order_by("order")
        return tasks[0] if tasks else None

    def last_task(self):
        tasks = self.task_set.order_by("-order")
        return tasks[0] if tasks else None

    def __str__(self):
        return _("Sessie {}").format(self.order)


class Task(models.Model):
    order = models.PositiveIntegerField()
    name = models.CharField(
        _("Wat is de naam van de taak?"),
        max_length=200,
        blank=True,
    )

    description = models.TextField(
        _(
            "Beschrijf de taak die de deelnemer moet uitvoeren, en leg kort "
            "uit hoe deze taak (en de eventuele manipulaties daarbinnen) aan de "
            "beantwoording van jouw onderzoeksvragen bijdraagt. "
            "Geef, kort, een paar voorbeelden (of beschrijvingen) van het type stimuli "
            "of prompts dat je van plan bent aan de deelnemer aan te bieden. Het moet "
            "voor de commissieleden duidelijk zijn wat je precies gaat doen."
        ),
        blank=True,
    )

    repeats = models.PositiveBigIntegerField(
        _("Hoe vaak voert een deelnemer deze taak uit binnen deze sessie?"),
        help_text=_(
            "Het kan zijn dat eenzelfde taak meerdere keren moet worden \
                    uitgevoerd binnen een sessie. Als dit het geval is, kun je dat hier \
                    aangeven. Als er variatie zit in de verschillende \
                    taken van deze sessie, maak dan een nieuwe taak \
                    aan voor elke unieke taak binnen deze sessie."
        ),
        null=False,
        default=1,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(100),
        ],  # Max of 100 is a technical safeguard
    )

    duration = models.PositiveIntegerField(
        _(
            "Wat is de duur van deze taak van begin tot eind in <strong>minuten</strong>, \
dus vanaf het moment dat de taak van start gaat tot en met het einde van de taak \
(exclusief instructie maar inclusief oefensessie)? \
Indien de taakduur per deelnemer varieert (self-paced taak of task-to-criterion), \
geef dan <strong>het redelijkerwijs te verwachten maximum op</strong>."
        ),
        default=0,
        validators=[MinValueValidator(1)],
        blank=True,
    )

    feedback = models.BooleanField(
        _(
            "Krijgen deelnemers tijdens of na deze taak feedback op hun "
            "gedrag of toestand?"
        ),
        null=True,
        blank=True,
    )

    feedback_details = models.TextField(
        _("Beschrijf hoe de feedback wordt gegeven."),
        blank=True,
    )

    # References
    session = models.ForeignKey(Session, on_delete=models.CASCADE)

    class Meta:
        ordering = ["order"]
        unique_together = ("session", "order")

    def delete(self, *args, **kwargs):
        """
        Invalidate the totals on Session level on deletion of a Task.
        """
        session = self.session
        session.tasks_duration = None
        super(Task, self).delete(*args, **kwargs)
        session.save()

    def __str__(self):
        return _("Taak {} in sessie {}").format(self.order, self.session.order)
