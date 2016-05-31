from django.core.exceptions import ValidationError
from django.db import models
from django.test import TestCase

from .utils import is_empty
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


class UtilsTest(TestCase):
    def test_is_empty(self):
        self.assertTrue(is_empty(None))
        self.assertFalse(is_empty(True))
        self.assertFalse(is_empty(False))

        self.assertTrue(is_empty(u''))
        self.assertTrue(is_empty(u'  '))
        self.assertFalse(is_empty(u' test '))
