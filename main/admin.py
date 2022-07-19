from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin
from django.contrib.auth.models import Group
from django.db.models import CharField
from django.forms import Textarea

from .models import Setting, SystemMessage

admin.site.unregister(Group)


class UserInLine(admin.TabularInline):
    model = Group.user_set.through
    extra = 0


@admin.register(Group)
class GenericGroup(GroupAdmin):
    inlines = [UserInLine]


@admin.register(Setting)
class SettingAdmin(admin.ModelAdmin):
    list_display = ('order', 'description', 'is_local', 'needs_details', 'needs_supervision', 'requires_review', 'is_school',)
    list_display_links = ('description', )
    ordering = ['order']


@admin.register(SystemMessage)
class SystemMessageAdmin(admin.ModelAdmin):
    list_display = ('level', 'message', 'not_before', 'not_after')
    list_display_links =  ('message', )
    ordering = ['not_before', 'not_after']
    formfield_overrides = {
        CharField: {'widget': Textarea}
    }
