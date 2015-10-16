from django.contrib import admin

from .models import Relation, AgeGroup, Trait, Registration, RegistrationKind, \
    Setting, Compensation, Recruitment, Faq, Member, Meeting


@admin.register(Relation)
class RelationAdmin(admin.ModelAdmin):
    list_display = ('order', 'description', 'needs_supervisor', )
    ordering = ['order']


@admin.register(AgeGroup)
class AgeGroupAdmin(admin.ModelAdmin):
    list_display = ('description', 'age_min', 'age_max', )
    ordering = ['age_min']


@admin.register(Trait)
class TraitAdmin(admin.ModelAdmin):
    list_display = ('order', 'description', 'needs_details', )
    ordering = ['order']


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


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('title', 'first_name', 'last_name', 'role', )
    ordering = ['first_name', 'last_name']


@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ('date', 'deadline', )
    ordering = ['date']
