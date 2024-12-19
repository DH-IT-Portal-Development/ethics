from django.contrib import admin

from .models import Registration


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = (
        "order",
        "description",
        "needs_details",
        "requires_review",
        "is_recording",
    )
    list_display_links = ("description",)
    ordering = ["order"]
