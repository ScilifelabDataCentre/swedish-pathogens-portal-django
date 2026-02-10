"""Admin configuration for Article app."""

from django.contrib import admin, messages
from django.db.models import QuerySet
from django.http import HttpRequest

from .models import HighlightsAndEditorials


@admin.register(HighlightsAndEditorials)
class HighlightsAndEditorialsAdmin(admin.ModelAdmin):
    """Admin interface for HighlightsAndEditorials model.

    Provides a comprehensive admin interface for managing articles
    (data highlights and editorials) with organised fieldsets, search
    functionality, filtering, and bulk actions.

    Features:
        - List display with title, type, slug, status, and timestamps
        - Filtering by active status, type, creation date, update date, and topics
        - Search by title, summary, content, announcement, tags, and author
        - Auto-populated slug field from title
        - Horizontal filter widget for topic selection
        - Bulk actions for activating/deactivating articles
        - Organised fieldsets for better UX
    """

    list_display = ["title", "type", "slug", "is_active", "created_at", "updated_at"]
    list_filter = ["is_active", "type", "created_at", "updated_at", "topics"]
    search_fields = ["title", "summary", "content", "announcement", "tags", "author"]
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ["updated_at"]
    filter_horizontal = ["topics"]
    actions = ["activate_articles", "deactivate_articles"]

    fieldsets = (
        (
            "Basic Information",
            {"fields": ("type", "title", "slug", "summary", "author")},
        ),
        ("Content", {"fields": ("content", "announcement")}),
        ("Categorization", {"fields": ("topics", "tags")}),
        ("Media", {"fields": ("featured_image", "figure_caption")}),
        ("Status", {"fields": ("is_active",)}),
        (
            "Timestamps",
            {
                "fields": ("created_at", "updated_at"),
            },
        ),
    )

    def activate_articles(self, request: HttpRequest, queryset: QuerySet) -> None:
        """Activate selected articles."""
        updated = queryset.update(is_active=True)
        self.message_user(
            request, f"Successfully activated {updated} article(s).", messages.SUCCESS
        )

    activate_articles.short_description = "Activate selected articles"

    def deactivate_articles(self, request: HttpRequest, queryset: QuerySet) -> None:
        """Deactivate selected articles."""
        updated = queryset.update(is_active=False)
        self.message_user(
            request, f"Successfully deactivated {updated} article(s).", messages.SUCCESS
        )

    deactivate_articles.short_description = "Deactivate selected articles"
