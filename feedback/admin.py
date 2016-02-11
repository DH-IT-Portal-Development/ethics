from django.contrib import admin

from .models import Feedback, Faq


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    fields = ('url', 'comment', 'submitter', 'priority', 'status')
    list_display = ['url', 'comment', 'submitter', 'date_created']
    list_filter = ('priority', 'status')


@admin.register(Faq)
class FaqAdmin(admin.ModelAdmin):
    list_display = ('order', 'question', )
    ordering = ['order']
