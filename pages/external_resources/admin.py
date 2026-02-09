"""Admin configuration for external resources."""

from django import forms
from django.contrib import admin, messages
from django.db.models import QuerySet
from django.http import HttpRequest

from .models import ExternalResource


class ExternalResourceAdminForm(forms.ModelForm):
    """Admin form for ExternalResource with multi-select data types."""

    data_type = forms.MultipleChoiceField(
        choices=ExternalResource.DataTypeChoices.choices,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        """Form metadata."""

        model = ExternalResource
        fields = [
            "name",
            "slug",
            "category",
            "data_type",
            "description",
            "keywords",
            "contact",
            "link",
            "thumbnail_image",
            "is_active",
        ]


class DataTypeListFilter(admin.SimpleListFilter):
    """Human-readable data type filter for ArrayField values."""

    title = "data type"
    parameter_name = "data_type"

    def lookups(
        self,
        request: HttpRequest,
        model_admin: admin.ModelAdmin,
    ) -> list[tuple[str, str]]:
        """Return readable data type choices."""
        return ExternalResource.DataTypeChoices.choices

    def queryset(
        self,
        request: HttpRequest,
        queryset: QuerySet[ExternalResource],
    ) -> QuerySet[ExternalResource]:
        """Filter queryset by selected data type."""
        value = self.value()
        if not value:
            return queryset
        return queryset.filter(data_type__contains=[value])


@admin.register(ExternalResource)
class ExternalResourceAdmin(admin.ModelAdmin):
    """Admin interface for external resources.

    Provides a comprehensive admin interface for managing external resources
    with organised fieldsets, search functionality, filtering, and bulk actions.
    """

    form = ExternalResourceAdminForm
    list_display = ["name", "category", "data_types_label", "is_active", "created_at"]
    list_filter = ["category", DataTypeListFilter, "is_active", "created_at"]
    search_fields = ["name", "description", "contact", "keywords"]
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ["created_at", "updated_at"]
    actions = ["activate_projects", "deactivate_projects"]

    fieldsets = (
        ("Basic Information", {"fields": ("name", "slug", "category", "data_type")}),
        ("Content", {"fields": ("description", "keywords", "contact", "link")}),
        ("Visual", {"fields": ("thumbnail_image",)}),
        ("Status", {"fields": ("is_active",)}),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    @admin.display(description="Data types")
    def data_types_label(self, obj: ExternalResource) -> str:
        """Return a comma-separated list of data types."""
        return obj.data_type_display

    def activate_projects(self, request: HttpRequest, queryset: QuerySet[ExternalResource]) -> None:
        """Activate selected projects."""
        updated = queryset.update(is_active=True)
        self.message_user(
            request, f"Successfully activated {updated} project(s).", messages.SUCCESS
        )

    activate_projects.short_description = "Activate selected projects"

    def deactivate_projects(
        self, request: HttpRequest, queryset: QuerySet[ExternalResource]
    ) -> None:
        """Deactivate selected projects."""
        updated = queryset.update(is_active=False)
        self.message_user(
            request, f"Successfully deactivated {updated} project(s).", messages.SUCCESS
        )

    deactivate_projects.short_description = "Deactivate selected projects"
