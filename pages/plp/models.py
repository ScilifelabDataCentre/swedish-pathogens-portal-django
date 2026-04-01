"""Models for the Pandemic Laboratory Preparedness (PLP) app."""

import markdown
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.text import slugify


class PlpProject(models.Model):
    """PLP project model for project listings and detail pages.

    Represents a pandemic preparedness capability project within the SciLifeLab
    Pandemic Laboratory Preparedness (PLP) program. These projects focus on
    developing services or resources that can be used in current and future
    pandemics.

    Attributes:
        title (str): Project title (e.g. 'Multi-disease serology').
        slug (str): URL-friendly identifier.
        category (str): Project category (e.g. PLP1, PLP2, TDP).
        content (str): Full markdown content for the project detail page.
        image (ImageField): Featured image for the project.
        created_at (datetime): Creation timestamp (defaults to now).
        updated_at (datetime): Timestamp when project was last modified.
        is_active (bool): Toggle visibility without deleting the record.
    """

    CATEGORY_CHOICES = [
        ("tdp2", "TDP2"),
        ("tdp", "TDP"),
        ("pmt", "PM TDP"),
        ("test", "PLP-Test"),
        ("plp2", "PLP2"),
        ("plp1", "PLP1"),
    ]
    CATEGORY_GROUP_LABELS = {
        "tdp2": "Technology Development Projects 2025 (PLP TDPs)",
        "tdp": "Technology Development Projects",
        "pmt": "Precision Medicine Technology Development Projects",
        "test": "Testing PLP Capabilities",
        "plp2": "Pandemic Laboratory Preparedness Capabilities round 2 2022",
        "plp1": "Pandemic Laboratory Preparedness Capabilities round 1",
    }

    # Basic fields
    title = models.CharField(
        max_length=255,
        unique=True,
        help_text="Project title (e.g. 'Multi-disease serology')",
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        help_text="URL-friendly version of the title (auto-generated from title)",
    )
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        help_text="Project category (e.g. PLP1, PLP2, TDP)",
    )

    # Media field
    image = models.ImageField(
        upload_to="plp/projects/",
        help_text="Featured image for the project",
    )

    # Content field
    content = models.TextField(help_text="Full markdown content for the project detail page")

    # Status field
    is_active = models.BooleanField(
        default=True, help_text="Toggle visibility without deleting the record"
    )

    # Timestamps
    created_at = models.DateTimeField(
        default=timezone.now, help_text="Creation timestamp (defaults to now)"
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Metadata for PLP project model."""

        ordering = ["-created_at"]
        verbose_name = "PLP Project"
        verbose_name_plural = "PLP Projects"

    def __str__(self) -> str:
        """Return the project title for string representation."""
        return self.title

    def save(self, *args: tuple, **kwargs: dict) -> None:
        """Save the project, auto-generating slug if not provided."""
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self) -> str:
        """Return the absolute URL for the project detail page."""
        return reverse("plp:detail", kwargs={"slug": self.slug})

    def get_category_group_label(self) -> str:
        """Return the display label for category group headings."""
        return self.CATEGORY_GROUP_LABELS.get(self.category, self.get_category_display())

    @property
    def image_url(self) -> str:
        """Return the URL of the image."""
        return self.image.url

    @property
    def rendered_content(self) -> str:
        """Return content rendered as HTML from markdown.

        Uses markdown library with common extensions for rich text rendering.
        """
        return mark_safe(
            markdown.markdown(self.content, extensions=["extra", "codehilite", "nl2br"])
        )
