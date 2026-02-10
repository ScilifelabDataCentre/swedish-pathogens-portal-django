"""Admin configuration for the outbreaks app."""

from django.contrib import admin, messages
from django.db.models import QuerySet
from django.http import HttpRequest

from .models import Outbreak


@admin.register(Outbreak)
class OutbreakAdmin(admin.ModelAdmin):
    """Admin interface for Outbreak model.

    Provides a comprehensive admin interface for managing outbreaks
    with organized fieldsets, search functionality, filtering, and bulk actions.

    Features:
        - List display with title, status, location, and timestamps
        - Filtering by status, active status, and location
        - Search by title, description, content, and location
        - Auto-populated slug field from title
        - Bulk actions for activating/deactivating outbreaks
        - Organized fieldsets for better UX
    """

    list_display = [
        "title",
        "status",
        "location",
        "is_active",
        "created_at",
        "updated_at",
    ]
    list_filter = ["status", "is_active", "location", "created_at", "updated_at"]
    search_fields = ["title", "description", "content", "location"]
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ["created_at", "updated_at"]
    actions = ["activate_outbreaks", "deactivate_outbreaks"]

    fieldsets = (
        (
            "Basic Information",
            {"fields": ("title", "slug", "status", "description", "location")},
        ),
        ("Media", {"fields": ("image",)}),
        ("Content", {"fields": ("content",)}),
        ("Status", {"fields": ("is_active",)}),
        ("Timestamps", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    def activate_outbreaks(self, request: HttpRequest, queryset: QuerySet[Outbreak]) -> None:
        """Activate selected outbreaks."""
        updated = queryset.update(is_active=True)
        self.message_user(
            request, f"Successfully activated {updated} outbreak(s).", messages.SUCCESS
        )

    activate_outbreaks.short_description = "Activate selected outbreaks"

    def deactivate_outbreaks(self, request: HttpRequest, queryset: QuerySet[Outbreak]) -> None:
        """Deactivate selected outbreaks."""
        updated = queryset.update(is_active=False)
        self.message_user(
            request, f"Successfully deactivated {updated} outbreak(s).", messages.SUCCESS
        )

    deactivate_outbreaks.short_description = "Deactivate selected outbreaks"
