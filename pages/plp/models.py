from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.text import slugify
import markdown


class PlpProject(models.Model):
    """PLP project model for project listings and detail pages.

    Represents a pandemic preparedness capability project within the SciLifeLab
    Pandemic Laboratory Preparedness (PLP) program. These projects focus on
    developing services or resources that can be used in current and future
    pandemics.

    Attributes:
        title (str): Project title (e.g. 'Multi-disease serology').
        slug (str): URL-friendly identifier (auto-generated from title if blank).
        category (str): Project category (e.g. PLP1, PLP2, TDP).
        summary (str): Short blurb shown on cards and listings (plain text).
        content (str): Full markdown content for the project detail page.
        featured_image (ImageField): Featured image for the project.
        created_at (datetime): Creation timestamp (defaults to now).
        updated_at (datetime): Timestamp when project was last modified.
        is_active (bool): Toggle visibility without deleting the record.
    """

    CATEGORY_CHOICES = [
        ("plp1", "PLP1"),
        ("plp2", "PLP2"),
        ("tdp", "TDP"),
        ("test", "PLP-Test"),
        ("pmt", "PM TDP"),
    ]

    title = models.CharField(
        max_length=255,
        unique=True,
        help_text="Project title (e.g. 'Multi-disease serology')",
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        blank=True,
        help_text="URL-friendly identifier (auto-generated from title if blank)",
    )
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        help_text="Project category (e.g. PLP1, PLP2, TDP)",
    )
    summary = models.TextField(help_text="Short blurb shown on cards and listings (plain text)")
    content = models.TextField(help_text="Full markdown content for the project detail page")
    featured_image = models.ImageField(
        upload_to="plp/projects/",
        blank=True,
        null=True,
        help_text="Featured image for the project",
    )
    created_at = models.DateTimeField(
        default=timezone.now, help_text="Creation timestamp (defaults to now)"
    )
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(
        default=True, help_text="Toggle visibility without deleting the record"
    )

    class Meta:
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

    @property
    def rendered_content(self) -> str:
        """Return content rendered as HTML from markdown.

        Uses markdown library with common extensions for rich text rendering.
        """
        return mark_safe(
            markdown.markdown(self.content, extensions=["extra", "codehilite", "tables", "nl2br"])
        )

    def get_absolute_url(self) -> str:
        """Return the absolute URL for the project detail page."""
        return reverse("plp:detail", kwargs={"slug": self.slug})

    @property
    def display_image(self) -> str:
        """Return featured image URL or a default placeholder."""
        if self.featured_image and hasattr(self.featured_image, "url"):
            return self.featured_image.url
        return "/static/images/defaults/blue_microbes.png"
