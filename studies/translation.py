from modeltranslation.translator import register, TranslationOptions

from .models import (
    Registration,
    RegistrationKind,
    AgeGroup,
    Compensation,
    Recruitment,
    SpecialDetail,
    Trait,
)


@register(Registration)
class RegistrationTranslationOptions(TranslationOptions):
    fields = ("description",)


@register(RegistrationKind)
class RegistrationKindTranslationOptions(TranslationOptions):
    fields = ("description",)


@register(AgeGroup)
class AgeGroupTranslationOptions(TranslationOptions):
    fields = ("description",)


@register(Compensation)
class CompensationTranslationOptions(TranslationOptions):
    fields = ("description",)


@register(Recruitment)
class RecruitmentTranslationOptions(TranslationOptions):
    fields = ("description",)


@register(Trait)
class TraitTranslationOptions(TranslationOptions):
    fields = ("description",)


@register(SpecialDetail)
class SpecialDetailTranslationOptions(TranslationOptions):
    fields = ("description",)
