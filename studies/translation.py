from modeltranslation.translator import register, TranslationOptions

from .models import AgeGroup, Compensation, Recruitment, Trait


@register(AgeGroup)
class AgeGroupTranslationOptions(TranslationOptions):
    fields = ('description',)


@register(Compensation)
class CompensationTranslationOptions(TranslationOptions):
    fields = ('description',)


@register(Recruitment)
class RecruitmentTranslationOptions(TranslationOptions):
    fields = ('description',)


@register(Trait)
class TraitTranslationOptions(TranslationOptions):
    fields = ('description',)
