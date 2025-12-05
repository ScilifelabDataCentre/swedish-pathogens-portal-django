"""Admin interface for PublicationPathogens model."""

from django.contrib import admin, messages
from django.db.models import QuerySet
from django.http import HttpRequest

from .models import PublicationPathogens


@admin.register(PublicationPathogens)
class PublicationPathogensAdmin(admin.ModelAdmin):
    """Admin interface for PublicationPathogens model.

    Provides an organized admin interface for managing pathogens
    used to fetch recent publications.

    Features:
        - List display with name, active status, and creation date
        - Filtering by active status and creation date
        - Search by name
        - Read-only fields for timestamps
        - Organized fieldsets for better UX
        - Bulk actions for activating/deactivating pathogens
    """

    list_display = ["name", "is_active", "created_at"]
    list_filter = ["is_active", "created_at"]
    search_fields = ["name"]
    readonly_fields = ["created_at", "updated_at"]
    date_hierarchy = "created_at"
    ordering = ["name", "-created_at"]
    actions = ["activate_pathogens", "deactivate_pathogens"]

    fieldsets = (
        (
            "Pathogen Information",
            {"fields": ("name", "query_string")},
        ),
        (
            "Status",
            {"fields": ("is_active",)},
        ),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def activate_pathogens(
        self, request: HttpRequest, queryset: QuerySet[PublicationPathogens]
    ) -> None:
        """Activate selected pathogens."""
        updated = queryset.update(is_active=True)
        self.message_user(
            request, f"Successfully activated {updated} pathogen(s).", messages.SUCCESS
        )

    activate_pathogens.short_description = "Activate selected pathogens"

    def deactivate_pathogens(
        self, request: HttpRequest, queryset: QuerySet[PublicationPathogens]
    ) -> None:
        """Deactivate selected pathogens."""
        updated = queryset.update(is_active=False)
        self.message_user(
            request, f"Successfully deactivated {updated} pathogen(s).", messages.SUCCESS
        )

    deactivate_pathogens.short_description = "Deactivate selected pathogens"
