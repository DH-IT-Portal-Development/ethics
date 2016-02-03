from django.contrib import admin

from .models import Relation, AgeGroup, Registration, RegistrationKind, \
    Setting, Compensation, Recruitment, Faq


@admin.register(Relation)
class RelationAdmin(admin.ModelAdmin):
    list_display = ('order', 'description', 'needs_supervisor', )
    ordering = ['order']


@admin.register(AgeGroup)
class AgeGroupAdmin(admin.ModelAdmin):
    list_display = ('description', 'age_min', 'age_max', )
    ordering = ['age_min']


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ('order', 'description', 'needs_details', 'needs_kind', )
    ordering = ['order']


@admin.register(RegistrationKind)
class RegistrationKindAdmin(admin.ModelAdmin):
    list_display = ('registration', 'order', 'description', )
    ordering = ['registration', 'order']


@admin.register(Setting)
class SettingAdmin(admin.ModelAdmin):
    list_display = ('order', 'description', 'needs_details', )
    ordering = ['order']


@admin.register(Compensation)
class CompensationAdmin(admin.ModelAdmin):
    list_display = ('order', 'description', 'needs_details', )
    ordering = ['order']


@admin.register(Recruitment)
class RecruitmentAdmin(admin.ModelAdmin):
    list_display = ('order', 'description', 'needs_details', )
    ordering = ['order']


@admin.register(Faq)
class FaqAdmin(admin.ModelAdmin):
    list_display = ('order', 'question', )
    ordering = ['order']
