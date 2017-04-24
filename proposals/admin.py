from django.contrib import admin

from .models import Relation, Funding


@admin.register(Relation)
class RelationAdmin(admin.ModelAdmin):
    list_display = ('order', 'description', 'needs_supervisor', 'check_in_course', 'check_pre_assessment', )
    list_display_links = ('description', )
    ordering = ['order']


@admin.register(Funding)
class FundingAdmin(admin.ModelAdmin):
    list_display = ('order', 'description', 'needs_details', 'needs_name', 'requires_review', )
    list_display_links = ('description', )
    ordering = ['order']
