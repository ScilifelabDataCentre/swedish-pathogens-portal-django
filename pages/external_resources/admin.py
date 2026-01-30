"""Admin configuration for external resources."""

from django import forms
from django.contrib import admin
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
    """Admin interface for external resources."""

    form = ExternalResourceAdminForm
    list_display = ["name", "category", "data_types_label", "is_active", "created_at"]
    list_filter = ["category", DataTypeListFilter, "is_active", "created_at"]
    search_fields = ["name", "description", "contact", "keywords"]
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ["created_at", "updated_at"]

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
