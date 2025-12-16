"""Models for News page."""

import markdown
from django.db import models
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.text import slugify


class News(models.Model):
    """News model for adding portal updates.

    Represents news items that can be updates, announcements, etc.
    Each news can contain the following information

    Attributes:
        title (str): Display name of the News (max 200 chars, unique).
        slug (str): URL-friendly version of title (auto-generated).
        summary (str): Brief summary to be displayed in news index page.
        content (str): Rich markdown content for detail pages.
        image (ImageField): Image to be used in index and detail page.
        is_active (bool): Whether news is visible (default: True).
        created_at (datetime): When news was created.
        updated_at (datetime): When news was last updated.

    Example:
        Create a new News:

        .. code-block:: python

            news = News.objects.create(
                title="New highlight added",
                summary="A new data highlight was added...",
                content="The data highlight is about...",
                image="some_image.png"
            )
            # slug automatically generated as "new-highlight-added"

    """

    title = models.CharField(max_length=200, unique=True, help_text="Title of news item")
    slug = models.SlugField(
        max_length=200,
        unique=True,
        help_text="URL-friendly version of the title (auto-generated from Title)",
    )
    summary = models.TextField(help_text="Short summary for news index page")
    content = models.TextField(
        help_text="Rich text content in markdown format (displayed on news detail page)"
    )
    image = models.ImageField(
        upload_to="news/images/", help_text="Image to be used in index and detail page"
    )
    is_active = models.BooleanField(
        default=True, help_text="Whether this news is active and visible"
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        help_text="Creation date (defaults to current date if not provided)",
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Metadata for News model."""

        ordering = ["-created_at"]
        verbose_name = "News"
        verbose_name_plural = "News"

    def __str__(self) -> str:
        """Return the string representation of News."""
        return self.title

    def save(self, *args, **kwargs) -> None:
        """Save the news, auto-generating slug if not provided."""
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    @property
    def rendered_content(self) -> str:
        """Return content rendered as HTML from markdown."""
        return mark_safe(markdown.markdown(self.content, extensions=["extra", "codehilite"]))
