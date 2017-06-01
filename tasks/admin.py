from django.contrib import admin

from .models import Registration, RegistrationKind


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ('order', 'description', 'is_local', 'needs_details', 'needs_kind', 'requires_review', 'age_min', )
    list_display_links = ('description', )
    ordering = ['order']


@admin.register(RegistrationKind)
class RegistrationKindAdmin(admin.ModelAdmin):
    list_display = ('registration', 'order', 'description', 'needs_details', 'requires_review', )
    list_display_links = ('description', )
    ordering = ['registration', 'order']
