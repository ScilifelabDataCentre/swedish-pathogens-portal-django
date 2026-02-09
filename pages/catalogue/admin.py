"""Admin configuration for catalogue."""

from django import forms
from django.contrib import admin, messages
from django.db.models import QuerySet
from django.http import HttpRequest

from .models import Catalogue


class CatalogueAdminForm(forms.ModelForm):
    """Admin form for Catalogue with multi-select fields."""

    category = forms.MultipleChoiceField(
        choices=Catalogue.CategoryChoices.choices,
        widget=forms.CheckboxSelectMultiple,
    )
    data_type = forms.MultipleChoiceField(
        choices=Catalogue.DataTypeChoices.choices,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        """Form metadata."""

        model = Catalogue
        fields = [
            "name",
            "category",
            "data_type",
            "description",
            "keywords",
            "link",
            "thumbnail_image",
            "is_active",
        ]


class ArrayFieldListFilter(admin.SimpleListFilter):
    """Reusable list filter for ArrayField values."""

    choices_class = None
    array_field_name = None

    def lookups(
        self,
        request: HttpRequest,
        model_admin: admin.ModelAdmin,
    ) -> list[tuple[str, str]]:
        """Return readable choices for the filter."""
        return self.choices_class.choices

    def queryset(
        self,
        request: HttpRequest,
        queryset: QuerySet[Catalogue],
    ) -> QuerySet[Catalogue]:
        """Filter queryset by selected value using array containment."""
        value = self.value()
        if not value:
            return queryset
        return queryset.filter(**{f"{self.array_field_name}__contains": [value]})


class CategoryListFilter(ArrayFieldListFilter):
    """Filter catalogue entries by category."""

    title = "category"
    parameter_name = "category"
    choices_class = Catalogue.CategoryChoices
    array_field_name = "category"


class DataTypeListFilter(ArrayFieldListFilter):
    """Filter catalogue entries by data type."""

    title = "data type"
    parameter_name = "data_type"
    choices_class = Catalogue.DataTypeChoices
    array_field_name = "data_type"


@admin.register(Catalogue)
class CatalogueAdmin(admin.ModelAdmin):
    """Admin interface for catalogue entries.

    Provides a comprehensive admin interface for managing catalogue entries
    with organised fieldsets, search functionality, filtering, and bulk actions.
    """

    form = CatalogueAdminForm
    list_display = ["name", "categories_label", "data_types_label", "is_active", "created_at"]
    list_filter = [CategoryListFilter, DataTypeListFilter, "is_active", "created_at"]
    search_fields = ["name", "description", "keywords"]
    readonly_fields = ["created_at", "updated_at"]
    actions = ["activate_entries", "deactivate_entries"]

    fieldsets = (
        ("Basic Information", {"fields": ("name", "category", "data_type")}),
        ("Content", {"fields": ("description", "keywords", "link")}),
        ("Visual", {"fields": ("thumbnail_image",)}),
        ("Status", {"fields": ("is_active",)}),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    @admin.display(description="Categories")
    def categories_label(self, obj: Catalogue) -> str:
        """Return a comma-separated list of categories."""
        return obj.category_display

    @admin.display(description="Data types")
    def data_types_label(self, obj: Catalogue) -> str:
        """Return a comma-separated list of data types."""
        return obj.data_type_display

    @admin.action(description="Activate selected entries")
    def activate_entries(self, request: HttpRequest, queryset: QuerySet[Catalogue]) -> None:
        """Activate selected entries."""
        updated = queryset.update(is_active=True)
        self.message_user(
            request, f"Successfully activated {updated} entry/entries.", messages.SUCCESS
        )

    @admin.action(description="Deactivate selected entries")
    def deactivate_entries(self, request: HttpRequest, queryset: QuerySet[Catalogue]) -> None:
        """Deactivate selected entries."""
        updated = queryset.update(is_active=False)
        self.message_user(
            request, f"Successfully deactivated {updated} entry/entries.", messages.SUCCESS
        )
