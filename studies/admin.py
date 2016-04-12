from django.contrib import admin

from .models import AgeGroup, Trait, Setting, Compensation, Recruitment


@admin.register(AgeGroup)
class AgeGroupAdmin(admin.ModelAdmin):
    list_display = ('description', 'age_min', 'age_max', )
    list_display_links = ('description', )
    ordering = ['age_min']


@admin.register(Trait)
class TraitAdmin(admin.ModelAdmin):
    list_display = ('order', 'description', 'needs_details', )
    ordering = ['order']


@admin.register(Setting)
class SettingAdmin(admin.ModelAdmin):
    list_display = ('order', 'description', 'needs_details', 'needs_supervision', 'requires_review', )
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
