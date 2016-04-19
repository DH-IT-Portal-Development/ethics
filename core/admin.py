from django.contrib import admin

from .models import Setting


@admin.register(Setting)
class SettingAdmin(admin.ModelAdmin):
    list_display = ('order', 'description', 'needs_details', 'needs_supervision', 'requires_review', )
    list_display_links = ('description', )
    ordering = ['order']
