from django.contrib import admin
from .models import Contact, Worker


# ==================== CONTACT ADMIN (FIXED) ====================

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ("name", "phone_number", "email", "created_at")
    search_fields = ("name", "phone_number", "email")
    ordering = ("-created_at",)


# ==================== WORKER ADMIN ====================

@admin.register(Worker)
class WorkerAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "skill",
        "location",
        "phone",
        "rating",
        "experience_years",
        "is_available"
    )

    search_fields = ("name", "skill", "location", "phone")
    list_filter = ("skill", "location", "is_available")

    ordering = ("-rating",)

    fieldsets = (
        ("Basic Info", {
            "fields": ("name", "skill", "location", "phone")
        }),
        ("Work Details", {
            "fields": ("experience_years", "rating", "is_available")
        }),
    )