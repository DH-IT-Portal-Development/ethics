from django.contrib import admin

from .models import Feedback


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    fields = ('url', 'comment', 'submitter', 'priority', 'status')
    list_display = ['url', 'comment', 'submitter', 'date_created']
    list_filter = ('priority', 'status')
