from django.contrib import admin

from .models import Review, Decision


class ReviewAdmin(admin.ModelAdmin):
    list_display = ('proposal', 'date_start', 'date_end', 'go')


class DecisionAdmin(admin.ModelAdmin):
    list_display = ('review', 'reviewer', 'go')

admin.site.register(Review, ReviewAdmin)
admin.site.register(Decision, DecisionAdmin)
