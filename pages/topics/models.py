"""Models for Topic page."""

import markdown
from django.db import models
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.text import slugify


class Topic(models.Model):
    r"""Topic model for categorizing portal content.

    Represents topics that can be associated with dashboards,
    data highlights, and other portal content. Each topic has a name,
    description, content, and thumbnail image.

    Attributes:
        title (str): Display name of the topic (max 100 chars, unique).
        slug (str): URL-friendly version of title (auto-generated).
        description (str): Brief description for topic cards.
        image (ImageField): Thumbnail image for topic cards.
        content (str): Rich markdown content for detail pages.
        announcement (str, optional): Prominent alert message for topic page.
        is_active (bool): Whether topic is visible (default: True).
        created_at (datetime): When topic was created.
        updated_at (datetime): When topic was last updated.

    Example:
        Create a new topic:

        .. code-block:: python

            topic = Topic.objects.create(
                title="COVID-19 Research",
                description="Research related to COVID-19",
                image="covid19.jpg",
                content="# COVID-19\n\nResearch content..."
            )
            # slug automatically generated as "covid-19-research"
    """

    # Basic fields
    title = models.CharField(
        max_length=100,
        unique=True,
        help_text="Title of the topic",
    )
    slug = models.SlugField(
        max_length=100,
        unique=True,
        help_text="URL-friendly version of the title (auto-generated from title)",
    )
    description = models.TextField(help_text="Description of the topic to display in the card")

    # Media field
    image = models.ImageField(
        upload_to="topics/images/",
        help_text="Thumbnail image for the topic card display",
    )

    # Content field
    content = models.TextField(
        help_text="Rich text content in markdown format (displayed on topic detail page)"
    )
    announcement = models.TextField(  # noqa: DJ001 # NOTE: ruff linting recommends removing null=True
        blank=True,
        null=True,
        help_text="Optional announcement message to display prominently on the topic page",
    )

    # Status field
    is_active = models.BooleanField(
        default=True, help_text="Whether this topic is active and visible"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Metadata for Topic model."""

        ordering = ["title"]
        verbose_name = "Topic"
        verbose_name_plural = "Topics"

    def __str__(self) -> str:
        """Return the topic title for string representation."""
        return self.title

    def save(self, *args, **kwargs) -> None:
        """Save the topic, auto-generating slug if not provided."""
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self) -> str:
        """Return the URL to access a particular topic instance."""
        return reverse("topics:detail", kwargs={"slug": self.slug})

    @property
    def image_url(self) -> str:
        """Return the URL of the thumbnail image."""
        return self.image.url

    @property
    def rendered_content(self) -> str:
        """Return content rendered as HTML from markdown."""
        return mark_safe(markdown.markdown(self.content, extensions=["extra", "codehilite"]))
