from django.db import models
from django.utils.translation import gettext_lazy as _


class Faq(models.Model):
    order = models.PositiveIntegerField(unique=True)
    question = models.TextField()
    answer = models.TextField()

    class Meta:
        verbose_name = _('FAQ')

    def __str__(self):
        return self.question
