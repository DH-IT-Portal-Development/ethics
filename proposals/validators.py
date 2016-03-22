from django.core.validators import BaseValidator
from django.utils.translation import ungettext_lazy


class MaxWordsValidator(BaseValidator):
    compare = lambda self, a, b: a > b
    clean = lambda self, x: len(x.split())
    message = ungettext_lazy(
        'Dit veld mag maximaal %(limit_value)d woord bevatten.',
        'Dit veld mag maximaal %(limit_value)d woorden bevatten.',
        'limit_value')
    code = 'max_words'
