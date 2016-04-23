from django.core.exceptions import ValidationError
from django.db import models
from django.test import TestCase

from .validators import MaxWordsValidator


class ValidatorTest(TestCase):
    def test_max_words_validator(self):
        class Mock(models.Model):
            test = models.TextField(validators=[MaxWordsValidator(5)])

        try:
            m = Mock(test='Dit is een test')
            m.full_clean()
        except ValidationError:
            self.fail()

        with self.assertRaises(ValidationError):
            m = Mock(test='Dit is een test die faalt')
            m.full_clean()
