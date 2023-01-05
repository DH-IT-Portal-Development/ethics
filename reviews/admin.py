from django.contrib import admin

from .models import Review, Decision


class DecisionInline(admin.StackedInline):
    model = Decision
    fields = ('reviewer', 'go')
    readonly_fields = ('reviewer', 'go')
    can_delete = False
    show_change_link = True

    def has_add_permission(self, request, obj):
        return False


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('proposal', 'date_start', 'date_end', 'go')
    list_filter = ('stage', 'continuation')
    search_fields = ('proposal__title',)
    inlines = (DecisionInline,)


@admin.register(Decision)
class DecisionAdmin(admin.ModelAdmin):
    list_display = ('review', 'reviewer', 'go')
    list_filter = ('go', )
    search_fields = (
        'reviewer__first_name',
        'reviewer__last_name',
        'reviewer__username',
        'review__proposal__title')
