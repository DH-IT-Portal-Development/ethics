from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin
from django.contrib.auth.models import Group

from .models import Setting

admin.site.unregister(Group)

class UserInLine(admin.TabularInline):
    model = Group.user_set.through
    extra = 0

@admin.register(Group)
class GenericGroup(GroupAdmin):
    inlines = [UserInLine]

@admin.register(Setting)
class SettingAdmin(admin.ModelAdmin):
    list_display = ('order', 'description', 'is_local', 'needs_details', 'needs_supervision', 'requires_review', )
    list_display_links = ('description', )
    ordering = ['order']
