from django.contrib import admin

from .models import Relation, Funding


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
