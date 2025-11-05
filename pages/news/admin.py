from django.contrib import admin
from .models import News


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    """Admin interface for News model.

    Provides a comprehensive admin interface for managing news
    with organized fieldsets, search functionality, and filtering.

    Features:
        - List display with title, slug, status, and creation date
        - Filtering by active status and creation date
        - Search by title and summary
        - Auto-populated slug field from title
        - Organized fieldsets for better UX
    """

    list_display = ["title", "slug", "created_at", "is_active"]
    list_filter = ["is_active", "created_at"]
    search_fields = ["title", "summary"]
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ["updated_at"]
    date_hierarchy = "created_at"
    ordering = ["-created_at"]

    fieldsets = (
        (
            "Basic Information",
            {"fields": ("title", "slug", "summary")},
        ),
        ("Content", {"fields": ("content",)}),
        ("Media", {"fields": ("image",)}),
        ("Status", {"fields": ("is_active",)}),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )
