from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.utils.safestring import mark_safe
from typing import List
import markdown
import re


class Outbreak(models.Model):
    """Outbreak model for tracking disease outbreaks affecting Sweden.

    Represents both current and historical disease outbreaks with comprehensive
    information about pathogens, transmission, timelines, and data visualizations.
    Each outbreak can be marked as current or historical and includes detailed
    background information and timeline data.

    Attributes:
        name (str): Display name of the outbreak (max 255 chars, unique).
        slug (str): URL-friendly version of name (auto-generated).
        status (str): "current" or "historical" - determines listing section.
        thumbnail_image (ImageField): Thumbnail image for cards.
        pathogen (str): Description of the pathogen in markdown format (used for card description).
        transmission (str): How the disease is transmitted in markdown format.
        sources_and_risk_factors (str): Sources and risk factors in markdown format.
        seasonality (str): Seasonal patterns if applicable in markdown format.
        brief_history (str): Brief history in markdown format.
        timeline_data (dict): Structured timeline data as JSON.
        data_visualization_links (str): Data visualization links in markdown format with listing text.
        location (str, optional): Geographic location.
        start_date (date, optional): When outbreak started.
        end_date (date, optional): When outbreak ended.
        is_active (bool): Whether outbreak is visible (default: True).
        created_at (datetime): When outbreak was created.
        updated_at (datetime): When outbreak was last updated.

    Example:
        Create a new outbreak:

        .. code-block:: python

            outbreak = Outbreak.objects.create(
                name="Hepatitis A (September 2025)",
                status="current",
                pathogen="Hepatitis A is a form of viral hepatitis...",
                transmission="The virus is commonly transmitted...",
                brief_history="On 20th November 2025...",
                location="Sweden",
                start_date="2025-09-01"
            )
            # slug automatically generated as "hepatitis-a-september-2025"
            # Note: Cards will use truncated pathogen field for description
    """

    STATUS_CHOICES = [
        ("current", "Current"),
        ("historical", "Historical"),
    ]

    # Required fields
    name = models.CharField(
        max_length=255,
        unique=True,
        help_text="Name of the outbreak (e.g., 'Hepatitis A (September 2025)')"
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        help_text="URL-friendly version of the name (auto-generated from name)"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="current",
        help_text="Whether this is a current or historical outbreak"
    )
    thumbnail_image = models.ImageField(
        upload_to="outbreaks/images/",
        help_text="Thumbnail image for the outbreak card display"
    )

    # Background information fields (all markdown)
    pathogen = models.TextField(
        help_text="Description of the pathogen causing the outbreak in markdown format (used for card description)"
    )
    transmission = models.TextField(
        help_text="How the disease is transmitted in markdown format"
    )
    sources_and_risk_factors = models.TextField(
        help_text="Sources and risk factors for the outbreak in markdown format"
    )
    seasonality = models.TextField(
        blank=True,
        help_text="Seasonal patterns if applicable in markdown format (optional)"
    )

    # Content fields (all markdown)
    brief_history = models.TextField(
        help_text="Brief history of the outbreak in markdown format"
    )
    timeline_data = models.JSONField(
        default=list,
        blank=True,
        help_text="Structured timeline data as JSON array with 'year', 'date', 'observation' keys"
    )
    data_visualization_links = models.TextField(
        blank=True,
        help_text="Data visualization links in markdown format with listing text and links (e.g., '- [Link Text](https://example.com)')"
    )

    # Metadata fields
    location = models.CharField(
        max_length=255,
        blank=True,
        help_text="Geographic location (e.g., 'Sweden', 'International')"
    )
    start_date = models.DateField(
        null=True,
        blank=True,
        help_text="When the outbreak started (optional)"
    )
    end_date = models.DateField(
        null=True,
        blank=True,
        help_text="When the outbreak ended (null for current outbreaks)"
    )

    # Status field
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this outbreak is active and visible"
    )

    # Timestamps
    created_at = models.DateTimeField(
        default=timezone.now,
        help_text="Creation date (defaults to current date if not provided)"
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-start_date", "-created_at"]
        verbose_name = "Outbreak"
        verbose_name_plural = "Outbreaks"

    def __str__(self) -> str:
        """Return the outbreak name for string representation."""
        return self.name

    def save(self, *args, **kwargs):
        """Save the outbreak, auto-generating slug if not provided."""
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def display_image(self) -> str:
        """Return the URL of the thumbnail image."""
        return self.thumbnail_image.url

    @property
    def rendered_pathogen(self) -> str:
        """Return pathogen description rendered as HTML from markdown."""
        return mark_safe(
            markdown.markdown(self.pathogen, extensions=["extra", "codehilite"])
        )

    @property
    def rendered_transmission(self) -> str:
        """Return transmission description rendered as HTML from markdown."""
        return mark_safe(
            markdown.markdown(self.transmission, extensions=["extra", "codehilite"])
        )

    @property
    def rendered_sources_and_risk_factors(self) -> str:
        """Return sources and risk factors rendered as HTML from markdown."""
        return mark_safe(
            markdown.markdown(self.sources_and_risk_factors, extensions=["extra", "codehilite"])
        )

    @property
    def rendered_seasonality(self) -> str:
        """Return seasonality description rendered as HTML from markdown."""
        if not self.seasonality:
            return ""
        return mark_safe(
            markdown.markdown(self.seasonality, extensions=["extra", "codehilite"])
        )

    @property
    def rendered_brief_history(self) -> str:
        """Return brief history rendered as HTML from markdown."""
        return mark_safe(
            markdown.markdown(self.brief_history, extensions=["extra", "codehilite"])
        )

    @property
    def rendered_data_visualization_links(self) -> str:
        """Return data visualization links rendered as HTML from markdown."""
        if not self.data_visualization_links:
            return ""
        return mark_safe(
            markdown.markdown(self.data_visualization_links, extensions=["extra", "codehilite"])
        )

    @property
    def formatted_timeline(self) -> List[dict]:
        """Return timeline data as a formatted list for template rendering."""
        if not self.timeline_data:
            return []
        return self.timeline_data

    @property
    def card_description(self) -> str:
        """Return truncated pathogen description for card display (plain text).

        Strips markdown formatting and truncates to 150 characters for use
        in outbreak cards on the index page.

        Returns:
            str: Plain text description truncated to 150 characters
        """
        # Strip markdown formatting characters
        plain_text = re.sub(r'[#*_\[\]()]', '', self.pathogen)
        # Replace multiple newlines with single space
        plain_text = re.sub(r'\n+', ' ', plain_text).strip()
        # Truncate if needed
        if len(plain_text) > 150:
            return plain_text[:150] + "..."
        return plain_text
