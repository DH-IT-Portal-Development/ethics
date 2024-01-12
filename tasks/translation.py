from modeltranslation.translator import register, TranslationOptions

from .models import Registration, RegistrationKind


@register(Registration)
class RegistrationTranslationOptions(TranslationOptions):
    fields = ("description",)


@register(RegistrationKind)
class RegistrationKindTranslationOptions(TranslationOptions):
    fields = ("description",)
