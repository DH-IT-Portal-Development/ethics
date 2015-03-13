from django.conf import settings
from django.db import models
from reviews.models import Review

class Meeting(models.Model):
    review = models.ForeignKey(Review)

class TimeSlot(models.Model):
    start = models.DateTimeField()
    end = models.DateTimeField()
    meeting = models.ForeignKey(Meeting)

class Response(models.Model):
    responded = models.BooleanField(default=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    timeslot = models.ForeignKey(TimeSlot)
