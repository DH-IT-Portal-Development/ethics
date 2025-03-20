from django.contrib import admin

from .models import Registration, RegistrationKind, AgeGroup, Trait, Compensation, Recruitment, SpecialDetail

@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = (
        "order",
        "description",
        "is_local",
        "needs_details",
        "needs_kind",
        "requires_review",
        "age_min",
        "is_recording",
    )
    list_display_links = ("description",)
    ordering = ["order"]


@admin.register(RegistrationKind)
class RegistrationKindAdmin(admin.ModelAdmin):
    list_display = (
        "registration",
        "order",
        "description",
        "needs_details",
        "requires_review",
    )
    list_display_links = ("description",)
    ordering = ["registration", "order"]

@admin.register(AgeGroup)
class AgeGroupAdmin(admin.ModelAdmin):
    list_display = (
        "description",
        "age_min",
        "is_active",
        "age_max",
        "is_adult",
        "needs_details",
        "max_net_duration",
    )
    list_display_links = ("description",)
    ordering = ["age_min"]


@admin.register(Trait)
class TraitAdmin(admin.ModelAdmin):
    list_display = (
        "order",
        "description",
        "needs_details",
    )
    ordering = ["order"]


@admin.register(Compensation)
class CompensationAdmin(admin.ModelAdmin):
    list_display = (
        "order",
        "description",
        "needs_details",
        "requires_review",
    )
    list_display_links = ("description",)
    ordering = ["order"]


@admin.register(Recruitment)
class RecruitmentAdmin(admin.ModelAdmin):
    list_display = (
        "order",
        "description",
        "is_local",
        "needs_details",
        "requires_review",
    )
    list_display_links = ("description",)
    ordering = ["order"]


@admin.register(SpecialDetail)
class SpecialDetailAdmin(admin.ModelAdmin):
    list_display = ("order", "description", "medical_traits")
    list_display_links = ("description",)
    ordering = ["order"]
