from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import GroupAdmin, UserAdmin
from django.contrib.auth.models import Group
from django.db.models import CharField
from django.forms import Textarea

from .models import Setting, SystemMessage, Faculty

admin.site.unregister(Group)
admin.site.unregister(get_user_model())


class UserInLine(admin.TabularInline):
    model = Group.user_set.through
    extra = 0


@admin.register(Group)
class GenericGroup(GroupAdmin):
    inlines = [UserInLine]


@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ('saml_name', 'name', 'name_nl', 'name_en', 'internal_name',)
    list_display_links = ('saml_name',)
    filter_horizontal = ('users',)


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


class FacultyInline(admin.TabularInline):
    """Adds a 'Faculty' field to the User admin"""
    model = Faculty.users.through
    can_delete = False
    verbose_name_plural = "faculties"
    extra = 1


class CustomUserAdmin(UserAdmin):
    inlines = [FacultyInline]


admin.site.register(get_user_model(), CustomUserAdmin)