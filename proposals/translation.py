from modeltranslation.translator import register, TranslationOptions

from .models import Funding, Relation


@register(Funding)
class FundingTranslationOptions(TranslationOptions):
    fields = ('description',)


@register(Relation)
class RelationTranslationOptions(TranslationOptions):
    fields = ('description',)
