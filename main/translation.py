from modeltranslation.translator import register, TranslationOptions

from .models import Faculty, Setting, SystemMessage


@register(Setting)
class SettingTranslationOptions(TranslationOptions):
    fields = ('description',)


@register(SystemMessage)
class SystemMessageTranslationOptions(TranslationOptions):
    fields = ('message',)


@register(Faculty)
class FacultyTranslationOptions(TranslationOptions):
    fields = ('name',)
