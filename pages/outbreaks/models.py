"""Models for the outbreaks app."""

import markdown
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.text import slugify


class Outbreak(models.Model):
    r"""Outbreak model for tracking disease outbreaks affecting Sweden.

    Represents both current and historical disease outbreaks with comprehensive
    information. Each outbreak can be marked as current or historical and includes
    detailed background information in markdown format.

    Attributes:
        title (str): Display name of the outbreak (max 255 chars, unique).
        slug (str): URL-friendly version of title (auto-generated).
        status (str): "current" or "historical" - determines listing section.
        image (ImageField, optional): Thumbnail image for cards.
        description (str): Brief description for card display.
        content (str): Rich text content in markdown format (displayed on detail page).
        location (str, optional): Geographic location.
        is_active (bool): Whether outbreak is visible (default: True).
        created_at (datetime): When outbreak was created.
        updated_at (datetime): When outbreak was last updated.

    Example:
        Create a new outbreak:

        .. code-block:: python

            outbreak = Outbreak.objects.create(
                title="Hepatitis A (September 2025)",
                status="current",
                image="path/to/image.jpg",
                description="Brief description for card display",
                content="## Background\n\nFull markdown content...",
                location="Sweden"
            )
            # slug automatically generated as "hepatitis-a-september-2025"

    """

    STATUS_CHOICES = [
        ("current", "Current"),
        ("historical", "Historical"),
    ]

    # Basic fields
    title = models.CharField(
        max_length=255,
        unique=True,
        help_text="Title of the outbreak (e.g., 'Hepatitis A (September 2025)')",
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        blank=True,
        help_text="URL-friendly version of the name (auto-generated from name)",
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="current",
        help_text="Whether this is a current or historical outbreak",
    )
    description = models.TextField(
        help_text="Brief description of the outbreak to display in cards"
    )

    # Media field
    image = models.ImageField(
        upload_to="outbreaks/images/",
        help_text="Thumbnail image for the outbreak card display",
    )

    # Content fields
    content = models.TextField(
        help_text="Rich text content in markdown format (displayed on detail page)"
    )
    location = models.CharField(
        max_length=255,
        blank=True,
        help_text="Geographic location (e.g., 'Sweden', 'International')",
    )

    # Status field
    is_active = models.BooleanField(
        default=True, help_text="Whether this outbreak is active and visible"
    )

    # Timestamps
    created_at = models.DateTimeField(
        default=timezone.now, help_text="Creation date (defaults to current date if not provided)"
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Meta options for the Outbreak model."""

        ordering = ["-created_at"]
        verbose_name = "Outbreak"
        verbose_name_plural = "Outbreaks"

    def __str__(self) -> str:
        """Return the outbreak title for string representation."""
        return self.title

    def save(self, *args: tuple, **kwargs: dict) -> None:
        """Save the outbreak, auto-generating slug if not provided."""
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self) -> str:
        """Return the URL to access a detail page for this outbreak."""
        return reverse("outbreaks:detail", kwargs={"slug": self.slug})

    @property
    def image_url(self) -> str:
        """Return the URL of the image."""
        return self.image.url

    @property
    def rendered_content(self) -> str:
        """Return content rendered as HTML from markdown."""
        return mark_safe(  # noqa: S308
            markdown.markdown(self.content, extensions=["extra", "codehilite", "nl2br"])
        )
