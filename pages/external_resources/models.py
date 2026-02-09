"""Models for external resources."""

from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.validators import ArrayMinLengthValidator
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import models


def validate_contact_emails(value: str) -> None:
    """Validate one or more email addresses in a string."""
    if not value:
        return

    raw_items = [item.strip() for item in value.replace("\n", ",").split(",")]
    email_items = [item for item in raw_items if item]

    invalid_emails = []
    for email in email_items:
        try:
            validate_email(email)
        except ValidationError:
            invalid_emails.append(email)

    if invalid_emails:
        raise ValidationError(
            "Enter valid email address(es) separated by commas.",
        )


class ExternalResource(models.Model):
    """External resource entry for tools and data sources and repositories."""

    class DataTypeChoices(models.TextChoices):
        """Allowed data types for external resources."""

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
        """Page categories for external resources."""

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
        upload_to="external_resources/images/",
        help_text="Thumbnail image for the resource card",
    )
    contact = models.TextField(
        blank=True,
        validators=[validate_contact_emails],
        help_text="Optional contact email(s), separated by commas",
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
    category = models.CharField(
        max_length=50,
        choices=CategoryChoices.choices,
        help_text="Which page should display this resource",
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this resource is active and visible",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Metadata for ExternalResource model."""

        ordering = ["name"]
        verbose_name = "External resource"
        verbose_name_plural = "External resources"

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
