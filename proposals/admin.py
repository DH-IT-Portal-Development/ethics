from django.contrib import admin

from .models import Relation, Funding, AgeGroup, Registration, RegistrationKind, \
    Setting, Compensation, Recruitment


@admin.register(Relation)
class RelationAdmin(admin.ModelAdmin):
    list_display = ('order', 'description', 'needs_supervisor', )
    list_display_links = ('description', )
    ordering = ['order']


@admin.register(Funding)
class FundingAdmin(admin.ModelAdmin):
    list_display = ('order', 'description', 'needs_details', 'requires_review', )
    list_display_links = ('description', )
    ordering = ['order']


@admin.register(AgeGroup)
class AgeGroupAdmin(admin.ModelAdmin):
    list_display = ('description', 'age_min', 'age_max', )
    list_display_links = ('description', )
    ordering = ['age_min']


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ('order', 'description', 'needs_details', 'needs_kind', 'requires_review', 'age_min', )
    list_display_links = ('description', )
    ordering = ['order']


@admin.register(RegistrationKind)
class RegistrationKindAdmin(admin.ModelAdmin):
    list_display = ('registration', 'order', 'description', 'needs_details', 'requires_review', )
    list_display_links = ('description', )
    ordering = ['registration', 'order']


@admin.register(Setting)
class SettingAdmin(admin.ModelAdmin):
    list_display = ('order', 'description', 'needs_details', )
    list_display_links = ('description', )
    ordering = ['order']


@admin.register(Compensation)
class CompensationAdmin(admin.ModelAdmin):
    list_display = ('order', 'description', 'needs_details', )
    list_display_links = ('description', )
    ordering = ['order']


@admin.register(Recruitment)
class RecruitmentAdmin(admin.ModelAdmin):
    list_display = ('order', 'description', 'needs_details', )
    list_display_links = ('description', )
    ordering = ['order']
