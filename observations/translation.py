from modeltranslation.translator import register, TranslationOptions

from .models import Registration


@register(Registration)
class RegistrationTranslationOptions(TranslationOptions):
    fields = ('description',)
