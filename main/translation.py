from modeltranslation.translator import register, TranslationOptions

from .models import Setting


@register(Setting)
class SettingTranslationOptions(TranslationOptions):
    fields = ('description',)
