from django.conf import settings
from django.db import models
from django.core.urlresolvers import reverse

class Proposal(models.Model):
    DRAFT = 1
    WMO_AWAITING_DECISION = 2
    WMO_COMPLETED = 3
    STUDY_CREATED = 4
    TASKS_CREATED = 5
    INFORMED_CONSENT_UPLOADED = 6
    SUBMITTED = 7
    STATUSES = (
        (DRAFT, 'draft'),
        (WMO_AWAITING_DECISION, 'wmo_awaiting_decision'),
        (WMO_COMPLETED, 'wmo_finished'),
        (STUDY_CREATED, 'study'),
        (TASKS_CREATED, 'tasks'),
        (INFORMED_CONSENT_UPLOADED, 'informed_consent_uploaded'),
        (SUBMITTED, 'submitted'),
    )

    FUNCTIONS = (
        (1, '(PhD) student'),
        (2, 'post-doc'),
        (3, 'UD'),
        (4, 'professor'),
    )

    # Fields
    name = models.CharField(
        'Titel studie', 
        max_length=200, 
        help_text='Een studie wordt als volgt gedefinieerd: proefpersonen worden aan eenzelfde handeling of reeks handelingen onderworpen. \
Dus proefpersonen binnen de studie, ongeacht de groep (controle of  experimentele groep), doen allemaal dezelfde taak/taken. \
Wanneer het om herhaalde metingen gaat en de procedure verandert per meetmoment, moeten er verschillende aanvragen worden ingediend \
bij de commissie via deze webportal. Ook wanneer de taken onveranderd blijven, maar de proefpersonen kruisen een leeftijdscategorie \
(--link leeftijdscategorieen--), moeten er meerdere aanvragen ingediend worden. Vragen 6 en 7 gaan hierover. \
Het is handig voor het overzicht en het aanvraagproces om in de titel van de studie de leeftijdscategorie te vermelden.')
    tech_summary = models.TextField(
        'Samenvatting',
        help_text='Schrijf hier een samenvatting van max. 500 woorden. \
Deze samenvatting moet in ieder geval bestaan uit een duidelijke beschrijving van deonderzoeksvraag, de proefpersonen. \
Geef een helder beeld van de procedure en een beschrijving van de stimuli (indien daar sprake van is), \
het aantal taken en de methode waarmee het gedrag van de proefpersoon wordt vastgelegd \
(bijv.: reactietijden; knoppenbox; schriftelijke vragenlijst; interview; etc.).')
    longitudinal = models.BooleanField(
        'Is uw studie een longitudinale studie?',
        default=False)
    creator_function = models.CharField(
        'Functie', 
        max_length=1, 
        choices=FUNCTIONS)
    supervisor_name = models.CharField(
        'Naam eindverantwoordelijke',
        max_length=200, 
        help_text='De eindverantwoordelijke is een onderzoeker die de graad van doctor behaald heeft. \
Wanneer een student de aanvraag doet, dan is de eindverantwoordelijke de begeleidende onderzoeker met in ieder geval een doctorstitel.')
    supervisor_email = models.EmailField(
        'E-mailadres eindverantwoordelijke',
        help_text='Aan het einde van de procedure kunt u deze aanvraag ter verificatie naar uw eindverantwoordelijke sturen. \
Wanneer de verificatie binnen is, krijgt u een e-mail zodat u deze aanvraag kunt afronden.')
    informed_consent_pdf = models.FileField(
        'Upload hier de informed consent',
        blank=True)

    status = models.PositiveIntegerField(choices=STATUSES, default=DRAFT)

    # Dates 
    date_submitted = models.DateTimeField(null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    # References
    #created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='created_by')
    applicants = models.ManyToManyField(settings.AUTH_USER_MODEL, verbose_name='Uitvoerende(n)', related_name='applicants')
    parent = models.ForeignKey('self', null=True)

    def save(self, *args, **kwargs):
        """Sets the correct status on save of a Proposal"""
        self.status = self.get_status()
        super(Proposal, self).save(*args, **kwargs)

    def get_status(self):
        status = self.status
        if hasattr(self, 'wmo'): 
            wmo = self.wmo
            if wmo.metc or (wmo.is_medical and wmo.is_behavioristic):
                if not wmo.metc_decision: 
                    return self.WMO_AWAITING_DECISION
                if wmo.metc_decision and wmo.metc_decision_pdf: 
                    return self.WMO_COMPLETED
            else: 
                status = self.WMO_COMPLETED
        if hasattr(self, 'study'):
            status = self.STUDY_CREATED
        if self.task_set.all():
            status = self.TASKS_CREATED
        if self.informed_consent_pdf: 
            status = self.INFORMED_CONSENT_UPLOADED
        return status

    def continue_url(self): 
        if self.status == self.DRAFT:
            return reverse('proposals:wmo_create', args=(self.id,))
        if self.status == self.WMO_AWAITING_DECISION:
            return reverse('proposals:wmo_update', args=(self.id,))
        if self.status == self.WMO_COMPLETED:
            return reverse('proposals:study_create', args=(self.id,))
        if self.status == self.STUDY_CREATED:
            return reverse('proposals:task_create', args=(self.id,))
        if self.status == self.TASKS_CREATED:
            return reverse('proposals:consent', args=(self.id,))
        if self.status == self.INFORMED_CONSENT_UPLOADED:
            return reverse('proposals:submit', args=(self.id,))

    def __unicode__(self):
        return 'Proposal %s' % self.name

class Wmo(models.Model):
    metc = models.NullBooleanField(
        'Vindt de studie plaats binnen het UMC Utrecht, of een andere instelling waarbij de METC verplicht betrokken wordt?', 
        default=False)
    metc_institution = models.CharField(
        'Instelling',
        max_length=200,
        blank=True)
    is_medical = models.NullBooleanField(
        'Is de onderzoeksvraag medisch-wetenschappelijk van aard?', 
        default=False)
    is_behavioristic = models.NullBooleanField(
        'Worden de proefpersonen aan een handeling onderworpen of worden hen gedragsregels opgelegd?', 
        help_text='Een handeling of opgelegde gedragsregel varieert tussen het afnemen van weefsel bij een proefpersoon tot de proefpersoon een knop/toets in laten drukken.',
        default=False)
    metc_decision = models.BooleanField(
        'Is uw onderzoek al in behandeling genomen door een METC?',
        default=False)
    metc_decision_pdf = models.FileField(
        'Upload hier de beslissing van het METC',
        blank=True)

    # References
    proposal = models.OneToOneField(Proposal, primary_key=True)

    def save(self, *args, **kwargs):
        """Sets the correct status on save of a Proposal"""
        self.proposal.save()
        super(Wmo, self).save(*args, **kwargs)

    def __unicode__(self):
        return 'Wmo %s' % self.proposal.name

class AgeGroup(models.Model):
    age_min = models.PositiveIntegerField()
    age_max = models.PositiveIntegerField(blank=True, null=True)
    description = models.CharField(max_length=200)

    def __unicode__(self):
        if self.age_max: 
            return '%d-%d' % (self.age_min, self.age_max)
        else:
            return '%d+' % (self.age_min)

class Trait(models.Model):
    order = models.PositiveIntegerField(unique=True)
    description = models.CharField(max_length=200)
    needs_details = models.BooleanField(default=False)

    def __unicode__(self):
        return self.description

class Survey(models.Model):
    name = models.CharField(max_length=200)
    minutes = models.PositiveIntegerField()

    def __unicode__(self):
        return self.name

class Setting(models.Model):
    order = models.PositiveIntegerField(unique=True)
    description = models.CharField(max_length=200)
    needs_details = models.BooleanField(default=False)

    def __unicode__(self):
        return self.description

class Recruitment(models.Model):
    order = models.PositiveIntegerField(unique=True)
    description = models.CharField(max_length=200)
    needs_details = models.BooleanField(default=False)

    def __unicode__(self):
        return self.description

class Study(models.Model): 
    age_groups = models.ManyToManyField(
        AgeGroup, 
        verbose_name='Geef hieronder aan binnen welke leeftijdscategorie uw proefpersonen vallen, er zijn meerdere antwoorden zijn mogelijk')
    traits = models.ManyToManyField(
        Trait, 
        verbose_name='Worden de beoogde proefpersonen op bijzondere kenmerken geselecteerden die mogelijk een negatief effect hebben \
op de kwetsbaarheid of verminderde belastbaarheid van de proefpersoon? Indien u twee (of meer) groepen voor ogen heeft, \
hoeft u over de controlegroep (die dus geen bijzondere kenmerken heeft) niet in het hoofd te nemen bij het beantwoorden van de ze vraag')
    traits_details = models.CharField(
        'Namelijk', 
        max_length=200,
        blank=True)
    necessity = models.NullBooleanField(
        'Is het noodzakelijk om deze geselecteerde groep proefpersonen aan de door jou opgelegde handeling te onderwerpen om de onderzoeksvraag beantwoord te krijgen? \
Is het bijvoorbeeld noodzakelijk om kinderen te testen, of zou je de vraag ook kunnen beantwoorden door volwassen proefpersonen te testen?',
        default=True)
    necessity_reason = models.TextField(
        'Leg uit waarom',
        blank=True)
    setting = models.ManyToManyField(
        Setting,
        verbose_name='Geef aan waar de studie plaatsvindt')
    setting_details = models.CharField(
        'Namelijk', 
        max_length=200,
        blank=True)
    surveys = models.ManyToManyField(Survey)
    risk_physical = models.NullBooleanField(
        'Is de kans dat de proefpersoon fysiek letsel oploopt tijdens het afnemen van het experiment groter dan de kans op letsel in het dagelijks leven?',
        default=False)
    risk_psychological = models.NullBooleanField(
        'Is de kans dat de proefpersoon psychisch letsel oploopt tijdens het afnemen van het experiment groter dan de kans op letsel in het dagelijks leven?',
        default=False)
    compensation = models.CharField(
        'Welke vergoeding krijgt de proefpersoon voor verrichte taken?',
        max_length=200,
        help_text='tekst over dat vergoeding in redelijke verhouding moet zijn met belasting pp. En kinderen geen geld')
    recruitment = models.ManyToManyField(
        Recruitment,
        verbose_name='Hoe worden de proefpersonen geworven?')
    recruitment_details = models.CharField(
        'Namelijk', 
        max_length=200, 
        blank=True)

    # References
    proposal = models.OneToOneField(Proposal, primary_key=True)

    def save(self, *args, **kwargs):
        """Sets the correct status on save of a Proposal"""
        self.proposal.save()
        super(Study, self).save(*args, **kwargs)

    def __unicode__(self):
        return 'Study details for proposal %s' % self.proposal.name

class Action(models.Model): 
    order = models.PositiveIntegerField(unique=True)
    description = models.CharField(max_length=200)
    info_text = models.TextField()

    def __unicode__(self):
        return self.description

class Registration(models.Model): 
    order = models.PositiveIntegerField(unique=True)
    description = models.CharField(max_length=200)
    needs_details = models.BooleanField(default=False)

    def __unicode__(self):
        return self.description

class Task(models.Model): 
    name = models.CharField(
        'Naam van de taak', 
        max_length=200)
    procedure = models.NullBooleanField(
        'Welk onderdeel, of welke combinatie van onderdelen, van de procedure zouden door de proefpersonen als \
belastend/onaangenaam ervaren kunnen worden?')
    duration = models.PositiveIntegerField(
        'Wat is de duur van de taak, waarbij de proefpersoon een handeling moet verrichten, van begin tot eind, \
dus vanaf het moment dat de taak van start gaat tot en met het einde van de taak?')
    actions = models.ManyToManyField(
        Action,
        verbose_name='Geef aan welke handeling de proefpersoon moet uitvoeren of aan welke gedragsregel de proefpersoon wordt onderworpen')
    registrations = models.ManyToManyField(
        Registration,
        verbose_name='Hoe worden de gegevens vastgelegd? Door middel van:')
    registrations_details = models.CharField(
        'Namelijk', 
        max_length=200, 
        blank=True)

    def save(self, *args, **kwargs):
        """Sets the correct status on save of a Proposal"""
        self.proposal.save()
        super(Task, self).save(*args, **kwargs)

    # References
    proposal = models.ForeignKey(Proposal)

class Faq(models.Model):
    order = models.PositiveIntegerField(unique=True)
    question = models.TextField()
    answer = models.TextField()

    class Meta: 
        verbose_name = 'FAQ'

    def __unicode__(self):
        return self.question

class Member(models.Model): 
    title = models.CharField(max_length=200, blank=True)
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    role = models.CharField(max_length=200)

    def __unicode__(self):
        return '%s %s' % (self.first_name, self.last_name)

class Meeting(models.Model):
    date = models.DateField()
    deadline = models.DateField()

    def __unicode__(self):
        return '%s' % (self.date)
