# -*- encoding: utf-8 -*-
from __future__ import unicode_literals
import logging

from django.conf import settings
from django.contrib.auth.models import Group
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from django.utils.functional import lazy
from django.utils.safestring import mark_safe

mark_safe_lazy = lazy(mark_safe, str)

from main.models import YesNoDoubt
from main.validators import MaxWordsValidator, validate_pdf_or_doc
from proposals.utils import available_urls, FilenameFactory, OverwriteStorage
from datetime import date, timedelta

logger = logging.getLogger(__name__)

SUMMARY_MAX_WORDS = 200
SELF_ASSESSMENT_MAX_WORDS = 1000
COMMENTS_MAX_WORDS = 1000
PROPOSAL_FILENAME = FilenameFactory("Proposal")
PREASSESSMENT_FILENAME = FilenameFactory("Preassessment")
DMP_FILENAME = FilenameFactory("DMP")
METC_DECISION_FILENAME = FilenameFactory("METC_Decision")
PRE_APPROVAL_FILENAME = FilenameFactory("Pre_Approval")


class Relation(models.Model):
    order = models.PositiveIntegerField(unique=True)
    description = models.CharField(max_length=200)
    needs_supervisor = models.BooleanField(default=True)
    check_in_course = models.BooleanField(default=True)
    check_pre_assessment = models.BooleanField(default=True)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.description


class StudentContext(models.Model):
    order = models.PositiveIntegerField(unique=True)
    description = models.CharField(max_length=200)
    needs_details = models.BooleanField(default=False)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.description


class Funding(models.Model):
    order = models.PositiveIntegerField(unique=True)
    description = models.CharField(max_length=200)
    needs_details = models.BooleanField(default=False)
    needs_name = models.BooleanField(default=True)
    requires_review = models.BooleanField(default=False)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.description


class Institution(models.Model):
    order = models.PositiveIntegerField(unique=True)
    description = models.CharField(max_length=200)
    reviewing_chamber = models.ForeignKey(
        Group,
        on_delete=models.PROTECT,
    )

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.description


class Wmo(models.Model):
    class WMOStatuses(models.IntegerChoices):
        NO_WMO = 0, _("Geen beoordeling door METC noodzakelijk")
        WAITING = 1, _("In afwachting beslissing METC")
        JUDGED = 2, _("Beslissing METC geüpload")

    metc = models.CharField(
        _(
            "Vindt de dataverzameling plaats binnen het UMC Utrecht of \
andere instelling waar toetsing door een METC verplicht is gesteld?"
        ),
        max_length=1,
        choices=YesNoDoubt.choices,
        blank=True,
        default=None,
    )

    metc_details = models.TextField(
        _("Licht toe"),
        blank=True,
    )

    metc_institution = models.CharField(
        _("Welke instelling?"),
        max_length=200,
        blank=True,
    )

    is_medical = models.CharField(
        _(
            "Is de onderzoeksvraag medisch-wetenschappelijk van aard \
(zoals gedefinieerd door de WMO)?"
        ),
        help_text=_(
            "De definitie van medisch-wetenschappelijk onderzoek is: \
Medisch-wetenschappelijk onderzoek is onderzoek dat als doel heeft het \
beantwoorden van een vraag op het gebied van ziekte en gezondheid \
(etiologie, pathogenese, verschijnselen/symptomen, diagnose, preventie, \
uitkomst of behandeling van ziekte), door het op systematische wijze \
vergaren en bestuderen van gegevens. Het onderzoek beoogt bij te dragen \
aan medische kennis die ook geldend is voor populaties buiten de directe \
onderzoekspopulatie. (CCMO-notitie, Definitie medisch-wetenschappelijk \
onderzoek, 2005, ccmo.nl)"
        ),
        max_length=1,
        choices=YesNoDoubt.choices,
        blank=True,
    )

    metc_application = models.BooleanField(
        _(
            "Je onderzoek moet beoordeeld worden door een METC, maar dient nog \
wel bij de FETC-GW te worden geregistreerd. Is dit onderzoek al aangemeld \
bij een METC?"
        ),
        default=False,
    )

    metc_decision = models.BooleanField(
        _("Is de METC al tot een beslissing gekomen?"),
        default=False,
    )

    metc_decision_pdf = models.FileField(
        _(
            "Upload hier de beslissing van het METC \
(in .pdf of .doc(x)-formaat)"
        ),
        blank=True,
        validators=[validate_pdf_or_doc],
        upload_to=METC_DECISION_FILENAME,
        storage=OverwriteStorage(),
    )

    # Status
    status = models.PositiveIntegerField(
        choices=WMOStatuses.choices,
        default=WMOStatuses.NO_WMO,
    )

    enforced_by_commission = models.BooleanField(default=False)

    # References
    proposal = models.OneToOneField(
        "proposals.Proposal",
        primary_key=True,
        on_delete=models.CASCADE,
    )

    def save(self, *args, **kwargs):
        """Sets the correct status on save of a WMO"""
        self.update_status()
        super(Wmo, self).save(*args, **kwargs)

    def update_status(self):
        if (
            self.metc == YesNoDoubt.YES
            or self.is_medical == YesNoDoubt.YES
            or self.enforced_by_commission
        ):
            if self.metc_decision and self.metc_decision_pdf:
                self.status = self.WMOStatuses.JUDGED
            else:
                self.status = self.WMOStatuses.WAITING
        else:
            self.status = self.WMOStatuses.NO_WMO

    def __str__(self):
        return _("WMO {title}, status {status}").format(
            title=self.proposal.title, status=self.status
        )
