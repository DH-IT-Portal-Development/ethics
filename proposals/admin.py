from django.contrib import admin
from .models import AgeGroup, Trait, Action, Registration, Faq, Member, Meeting

@admin.register(AgeGroup)
class AgeGroupAdmin(admin.ModelAdmin):
    list_display = ('description', 'age_min', 'age_max', )
    ordering = ['age_min']

@admin.register(Trait)
class TraitAdmin(admin.ModelAdmin):
    list_display = ('description', )
    ordering = ['description']

@admin.register(Action)
class ActionAdmin(admin.ModelAdmin):
    list_display = ('description', 'info_text')
    ordering = ['description']

@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ('description', )
    ordering = ['description']

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

