from django.contrib import admin
from reviews.models import Review, Decision

class ReviewAdmin(admin.ModelAdmin):
    list_display = ('proposal', 'status')

class DecisionAdmin(admin.ModelAdmin):
    list_display = ('review', 'reviewer', 'go')

admin.site.register(Review, ReviewAdmin)
admin.site.register(Decision, DecisionAdmin)
