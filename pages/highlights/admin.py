from django.contrib import admin
from django.contrib import messages
from .models import DataHighlight


@admin.register(DataHighlight)
class DataHighlightAdmin(admin.ModelAdmin):
    """Admin interface for DataHighlight model.

    Provides a comprehensive admin interface for managing data highlights
    with organized fieldsets, search functionality, filtering, and bulk actions.

    Features:
        - List display with title, slug, status, and timestamps
        - Filtering by active status, creation date, update date, and topics
        - Search by title, summary, content, announcement, and tags
        - Auto-populated slug field from title
        - Horizontal filter widget for topic selection
        - Bulk actions for activating/deactivating highlights
        - Organized fieldsets for better UX
    """
    list_display = ["title", "type", "slug", "is_active", "created_at", "updated_at"]
    list_filter = ["is_active", "type", "created_at", "updated_at", "topics"]
    search_fields = ["title", "summary", "content", "announcement", "tags", "author"]
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ["updated_at"]
    filter_horizontal = ["topics"]
    actions = ["activate_highlights", "deactivate_highlights"]
    
    fieldsets = (
        ("Basic Information", {
            "fields": ("type", "title", "slug", "summary", "author")
        }),
        ("Content", {
            "fields": ("content", "announcement")
        }),
        ("Categorization", {
            "fields": ("topics", "tags")
        }),
        ("Media", {
            "fields": ("featured_image", "figure_caption")
        }),
        ("Status", {
            "fields": ("is_active",)
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )
    
    def activate_highlights(self, request, queryset):
        """Activate selected highlights."""
        updated = queryset.update(is_active=True)
        self.message_user(
            request,
            f"Successfully activated {updated} highlight(s).",
            messages.SUCCESS
        )
    activate_highlights.short_description = "Activate selected highlights"
    
    def deactivate_highlights(self, request, queryset):
        """Deactivate selected highlights."""
        updated = queryset.update(is_active=False)
        self.message_user(
            request,
            f"Successfully deactivated {updated} highlight(s).",
            messages.SUCCESS
        )
    deactivate_highlights.short_description = "Deactivate selected highlights"


