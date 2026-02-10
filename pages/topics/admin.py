"""Admin configuration for Topic page."""

from django.contrib import admin

from .models import Topic


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    """Admin interface for Topic model.

    Provides a comprehensive admin interface for managing topics
    with organized fieldsets, search functionality, and filtering.

    Features:
        - List display with title, slug, status, and creation date
        - Filtering by active status and creation date
        - Search by title and description
        - Auto-populated slug field from name
        - Organized fieldsets for better UX
    """

    list_display = ["title", "slug", "is_active", "created_at"]
    list_filter = ["is_active", "created_at"]
    search_fields = ["title", "description"]
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ["created_at", "updated_at"]

    fieldsets = (
        ("Basic Information", {"fields": ("title", "slug", "description")}),
        ("Media", {"fields": ("image",)}),
        ("Content", {"fields": ("content", "announcement")}),
        ("Status", {"fields": ("is_active",)}),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )
