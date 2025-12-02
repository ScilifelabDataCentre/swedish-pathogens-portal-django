from django.contrib import admin
from django.contrib import messages
from .models import Outbreak


@admin.register(Outbreak)
class OutbreakAdmin(admin.ModelAdmin):
    """Admin interface for Outbreak model.

    Provides a comprehensive admin interface for managing outbreaks
    with organized fieldsets, search functionality, filtering, and bulk actions.

    Features:
        - List display with name, status, location, dates, and timestamps
        - Filtering by status, active status, location, and dates
        - Search by name, pathogen, location, and brief_history
        - Auto-populated slug field from name
        - Bulk actions for activating/deactivating outbreaks
        - Organized fieldsets for better UX
    """

    list_display = [
        "name",
        "status",
        "location",
        "start_date",
        "end_date",
        "is_active",
        "created_at",
        "updated_at"
    ]
    list_filter = [
        "status",
        "is_active",
        "location",
        "start_date",
        "created_at",
        "updated_at"
    ]
    search_fields = [
        "name",
        "description",
        "content",
        "location"
    ]
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ["created_at", "updated_at"]
    actions = ["activate_outbreaks", "deactivate_outbreaks"]

    fieldsets = (
        (
            "Basic Information",
            {
                "fields": (
                    "name",
                    "slug",
                    "status",
                    "thumbnail_image",
                    "location"
                )
            }
        ),
        (
            "Content",
            {
                "fields": (
                    "description",
                    "content"
                )
            }
        ),
        (
            "Dates",
            {
                "fields": ("start_date", "end_date")
            }
        ),
        (
            "Status",
            {
                "fields": ("is_active",)
            }
        ),
        (
            "Timestamps",
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",)
            }
        ),
    )

    def activate_outbreaks(self, request, queryset):
        """Activate selected outbreaks."""
        updated = queryset.update(is_active=True)
        self.message_user(
            request,
            f"Successfully activated {updated} outbreak(s).",
            messages.SUCCESS
        )

    activate_outbreaks.short_description = "Activate selected outbreaks"

    def deactivate_outbreaks(self, request, queryset):
        """Deactivate selected outbreaks."""
        updated = queryset.update(is_active=False)
        self.message_user(
            request,
            f"Successfully deactivated {updated} outbreak(s).",
            messages.SUCCESS
        )

    deactivate_outbreaks.short_description = "Deactivate selected outbreaks"
