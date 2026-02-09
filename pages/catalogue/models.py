"""Models for catalogue."""

from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.validators import ArrayMinLengthValidator
from django.db import models


class Catalogue(models.Model):
    """Catalogue for tools, data sources, and data repositories."""

    class DataTypeChoices(models.TextChoices):
        """Allowed data types for catalogue entries."""

        BIOCHEMISTRY = "Biochemistry", "Biochemistry"
        DRUG_DISCOVERY = "Drug discovery", "Drug discovery"
        GENOMICS_TRANSCRIPTOMICS = "Genomics & transcriptomics", "Genomics & transcriptomics"
        HEALTH = "Health", "Health"
        IMAGING = "Imaging", "Imaging"
        OTHER = "Other", "Other"
        PROTEIN = "Protein", "Protein"
        PUBLIC_HEALTH = "Public health", "Public health"
        SEROLOGY = "Serology", "Serology"
        SOCIAL_SCIENCE_HUMANITIES = "Social science and humanities", "Social science and humanities"

    class CategoryChoices(models.TextChoices):
        """Page categories for catalogue entries."""

        TOOLS_CATALOGUE = "tools_catalogue", "Tools catalogue"
        DATA_REPOSITORIES = "data_repositories", "Data repositories"
        DATA_SOURCES = "data_sources", "Data sources"

    name = models.CharField(
        max_length=150,
        unique=True,
        help_text="Name of the resource",
    )
    link = models.URLField(
        help_text="External link to the resource",
    )
    thumbnail_image = models.ImageField(
        upload_to="catalogue/images/",
        help_text="Thumbnail image for the resource card",
    )
    description = models.TextField(
        help_text="Description for the resource card",
    )
    data_type = ArrayField(
        models.CharField(
            max_length=50,
            choices=DataTypeChoices.choices,
        ),
        validators=[ArrayMinLengthValidator(1)],
        help_text="Data type classification (select one or more)",
    )
    keywords = models.TextField(
        blank=True,
        help_text="Optional keywords for the resource, separated by commas",
    )
    category = ArrayField(
        models.CharField(
            max_length=50,
            choices=CategoryChoices.choices,
        ),
        validators=[ArrayMinLengthValidator(1)],
        help_text="Which page(s) should display this resource (select one or more)",
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this resource is active and visible",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Metadata for Catalogue model."""

        ordering = ["name"]
        verbose_name = "Catalogue entry"
        verbose_name_plural = "Catalogue entries"

    def __str__(self) -> str:
        """Return resource name for string representation."""
        return self.name

    def save(self, *args, **kwargs) -> None:
        """Save the resource."""
        super().save(*args, **kwargs)

    @property
    def display_image(self) -> str:
        """Return the URL of the thumbnail image."""
        return self.thumbnail_image.url

    @property
    def category_display(self) -> str:
        """Return categories as a readable comma-separated string."""
        if not self.category:
            return ""
        label_map = dict(self.CategoryChoices.choices)
        return ", ".join(label_map.get(c, c) for c in self.category)

    @property
    def data_type_display(self) -> str:
        """Return data types as a readable comma-separated string."""
        if not self.data_type:
            return ""
        if isinstance(self.data_type, (list, tuple)):
            cleaned_parts = []
            for item in self.data_type:
                raw_item = str(item).strip()
                if raw_item.startswith("{") and raw_item.endswith("}"):
                    raw_item = raw_item[1:-1]
                split_parts = [
                    part.strip().strip('"') for part in raw_item.split(",") if part.strip()
                ]
                cleaned_parts.extend(split_parts or [raw_item])
            return ", ".join(cleaned_parts)

        raw_value = str(self.data_type).strip()
        if raw_value.startswith("{") and raw_value.endswith("}"):
            raw_value = raw_value[1:-1]
        parts = [part.strip().strip('"') for part in raw_value.split(",") if part.strip()]
        return ", ".join(parts)
