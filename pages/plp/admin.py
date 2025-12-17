from django.contrib import admin
from django.contrib import messages

from .models import PlpProject


@admin.register(PlpProject)
class PlpProjectAdmin(admin.ModelAdmin):
    """Admin interface for PlpProject model.

    Provides a comprehensive admin interface for managing PLP projects
    with organised fieldsets, search functionality, filtering, and bulk actions.
    """

    list_display = ("title", "category", "is_active", "created_at", "updated_at")
    list_filter = ("category", "is_active", "created_at", "updated_at")
    search_fields = ("title", "summary", "content")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("updated_at",)
    actions = ["activate_projects", "deactivate_projects"]

    fieldsets = (
        (
            "Basic Information",
            {"fields": ("title", "slug", "category", "summary")},
        ),
        ("Content", {"fields": ("content",)}),
        ("Media", {"fields": ("featured_image",)}),
        ("Status", {"fields": ("is_active",)}),
        (
            "Timestamps",
            {
                "fields": ("created_at", "updated_at"),
            },
        ),
    )

    def activate_projects(self, request, queryset):
        """Activate selected projects."""
        updated = queryset.update(is_active=True)
        self.message_user(
            request, f"Successfully activated {updated} project(s).", messages.SUCCESS
        )

    activate_projects.short_description = "Activate selected projects"

    def deactivate_projects(self, request, queryset):
        """Deactivate selected projects."""
        updated = queryset.update(is_active=False)
        self.message_user(
            request, f"Successfully deactivated {updated} project(s).", messages.SUCCESS
        )

    deactivate_projects.short_description = "Deactivate selected projects"
