from modeltranslation.translator import register, TranslationOptions

from .models import Funding, Relation, Institution, StudentContext


@register(Funding)
class FundingTranslationOptions(TranslationOptions):
    fields = ('description',)


@register(Institution)
class FundingTranslationOptions(TranslationOptions):
    fields = ('description',)


@register(Relation)
class RelationTranslationOptions(TranslationOptions):
    fields = ('description',)

@register(StudentContext)
class RelationTranslationOptions(TranslationOptions):
    fields = ('description',)
