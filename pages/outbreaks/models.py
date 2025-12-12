"""Models for the outbreaks app."""

import markdown
from django.db import models
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.text import slugify


class Outbreak(models.Model):
    r"""Outbreak model for tracking disease outbreaks affecting Sweden.

    Represents both current and historical disease outbreaks with comprehensive
    information. Each outbreak can be marked as current or historical and includes
    detailed background information in markdown format.

    Attributes:
        name (str): Display name of the outbreak (max 255 chars, unique).
        slug (str): URL-friendly version of name (auto-generated).
        status (str): "current" or "historical" - determines listing section.
        thumbnail_image (ImageField, optional): Thumbnail image for cards.
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
                name="Hepatitis A (September 2025)",
                status="current",
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

    name = models.CharField(
        max_length=255,
        unique=True,
        help_text="Name of the outbreak (e.g., 'Hepatitis A (September 2025)')",
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
    thumbnail_image = models.ImageField(
        upload_to="outbreaks/images/",
        blank=True,
        null=True,
        help_text="Thumbnail image for the outbreak card display (optional)",
    )

    description = models.TextField(
        help_text="Brief description of the outbreak to display in cards"
    )
    content = models.TextField(
        help_text="Rich text content in markdown format (displayed on detail page)"
    )

    location = models.CharField(
        max_length=255,
        blank=True,
        help_text="Geographic location (e.g., 'Sweden', 'International')",
    )

    is_active = models.BooleanField(
        default=True, help_text="Whether this outbreak is active and visible"
    )

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
        """Return the outbreak name for string representation."""
        return self.name

    def save(self, *args: tuple, **kwargs: dict) -> None:
        """Save the outbreak, auto-generating slug if not provided."""
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def display_image(self) -> str:
        """Return the URL of the thumbnail image or a placeholder."""
        if self.thumbnail_image and hasattr(self.thumbnail_image, "url"):
            return self.thumbnail_image.url
        return "/static/images/outbreak-placeholder.svg"

    @property
    def rendered_content(self) -> str:
        """Return content rendered as HTML from markdown."""
        return mark_safe(  # noqa: S308
            markdown.markdown(self.content, extensions=["extra", "codehilite", "tables", "nl2br"])
        )
