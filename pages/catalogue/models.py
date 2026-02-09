"""Models for catalogue."""

from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.validators import ArrayMinLengthValidator
from django.db import models


class Catalogue(models.Model):
    """Catalogue for tools, data sources, and data repositories."""

    class DataTypeChoices(models.TextChoices):
        """Allowed data types for catalogue entries."""

        BIOCHEMISTRY = "Biochemistry"
        DRUG_DISCOVERY = "Drug discovery"
        GENOMICS_TRANSCRIPTOMICS = "Genomics & transcriptomics"
        HEALTH = "Health"
        IMAGING = "Imaging"
        OTHER = "Other"
        PROTEIN = "Protein"
        PUBLIC_HEALTH = "Public health"
        SEROLOGY = "Serology"
        SOCIAL_SCIENCE_HUMANITIES = "Social science and humanities"

    class CategoryChoices(models.TextChoices):
        """Page categories for catalogue entries."""

        TOOLS_CATALOGUE = "Tools catalogue"
        DATA_REPOSITORIES = "Data repositories"
        DATA_SOURCES = "Data sources"

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
        label_map = dict(self.DataTypeChoices.choices)
        return ", ".join(label_map.get(dt, dt) for dt in self.data_type)
