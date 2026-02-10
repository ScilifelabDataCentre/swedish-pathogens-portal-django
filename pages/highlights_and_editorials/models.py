"""Models for the Article app."""

import markdown
from django.db import models
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.text import slugify


class HighlightsAndEditorials(models.Model):
    r"""Highlights and editorials model for showcasing research findings and editorial content.

    Represents articles (data highlights and editorials) that showcase important
    scientific findings, data insights, and editorial content for the Swedish
    Pathogens Portal. Each article includes comprehensive information about research
    projects and can be associated with multiple topics for better content
    organisation and discovery.

    Attributes:
        type (str): Content type - either "Editorial" or "Data Highlight".
        title (str): Display title of the article (max 255 chars, unique).
        slug (str): URL-friendly version of title (auto-generated from title).
        summary (str): Brief summary displayed in article cards.
        content (str): Full markdown content displayed on detail pages.
        announcement (str, optional): Prominent announcement message for articles.
        tags (str, optional): Comma-separated tags for content matching and search.
        author (str, optional): Author name or names for the article.
        featured_image (ImageField): Primary image displayed with the article.
        figure_caption (str, optional): Descriptive caption for the featured image.
        topics (ManyToMany, optional): Research topics associated with this article.
        is_active (bool): Whether article is visible to users (default: True).
        created_at (datetime): Timestamp when article was created (editable in admin).
        updated_at (datetime): Timestamp when article was last modified.

    Example:
        Create a new article:

        .. code-block:: python

            article = HighlightsAndEditorials.objects.create(
                type="data_highlight",
                title="Novel Pathogen Discovery in Swedish Waters",
                summary="Researchers discovered a new bacterial species...",
                content="# Research Findings\n\nDetailed findings...",
                featured_image="pathogen_discovery.jpg"
            )
            # slug automatically generated as "novel-pathogen-discovery-in-swedish-waters"

    """

    # Content type choices
    CONTENT_TYPE_CHOICES = [
        ("data_highlight", "Data Highlight"),
        ("editorial", "Editorial"),
    ]

    # Required fields
    type = models.CharField(
        max_length=50,
        choices=CONTENT_TYPE_CHOICES,
        default="data_highlight",
        help_text="Type of content: Data Highlight or Editorial",
    )
    title = models.CharField(max_length=255, unique=True, help_text="Title of the article")
    slug = models.SlugField(
        max_length=255,
        unique=True,
        help_text="URL-friendly version of the title (auto-generated from title)",
    )

    # Content fields
    summary = models.TextField(help_text="Brief summary of the article for display in cards")
    content = models.TextField(help_text="Full content in markdown format displayed on detail page")
    announcement = models.TextField(
        blank=True,
        help_text=(
            "Optional announcement message in markdown format displayed at the top of the article"
        ),
    )
    tags = models.TextField(
        blank=True,
        help_text="Comma-separated tags for related content matching and search",
    )
    author = models.CharField(
        max_length=255,
        blank=True,
        help_text="Author name or names for the article (optional)",
    )

    # Media fields
    featured_image = models.ImageField(
        upload_to="articles/images/", help_text="Featured image for the article"
    )
    figure_caption = models.TextField(
        blank=True, help_text="Caption for the featured image (optional)"
    )

    # Relationships
    topics = models.ManyToManyField(
        "topics.Topic",
        blank=True,
        help_text="Research topics associated with this article (optional)",
    )

    # Status field
    is_active = models.BooleanField(
        default=True, help_text="Whether this highlight is active and visible"
    )

    # Timestamps
    created_at = models.DateTimeField(
        default=timezone.now,
        help_text="Creation date (defaults to current date if not provided)",
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Metadata for HighlightsAndEditorials model."""

        ordering = ["-created_at"]
        verbose_name = "Article"
        verbose_name_plural = "Articles"

    def __str__(self) -> str:
        """Return the article title for string representation."""
        return self.title

    def save(self, *args, **kwargs) -> None:
        """Save the article, auto-generating slug if not provided."""
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    @property
    def rendered_content(self) -> str:
        """Return content rendered as HTML from markdown."""
        return mark_safe(markdown.markdown(self.content, extensions=["extra", "codehilite"]))

    @property
    def rendered_announcement(self) -> str:
        """Return announcement rendered as HTML from markdown."""
        if self.announcement:
            return mark_safe(
                markdown.markdown(self.announcement, extensions=["extra", "codehilite"])
            )
        return ""

    @property
    def tag_list(self) -> list[str]:
        """Return tags as a list of cleaned strings."""
        if not self.tags:
            return []
        return [tag.strip().lower() for tag in self.tags.split(",") if tag.strip()]

    def get_related_articles(
        self, limit: int = 4, threshold: float = 0.1
    ) -> list["HighlightsAndEditorials"]:
        """Get related articles based on tag similarity.

        Finds articles with similar tags using Jaccard similarity algorithm.
        Only considers articles of the same type (Data Highlight or Editorial).
        Considers all related articles regardless of creation date (past and future).
        Results are ordered by similarity score (highest first).

        Args:
            limit: Maximum number of related articles to return (default: 4)
            threshold: Minimum similarity threshold between 0.0 and 1.0 (default: 0.1)

        Returns:
            List of related articles ordered by similarity score

        Example:
            Get top 3 related articles with at least 20% similarity:

            .. code-block:: python

                related = article.get_related_articles(limit=3, threshold=0.2)
                for related_article in related:
                    print(related_article.title)

        """
        if not self.tag_list:
            return HighlightsAndEditorials.objects.none()

        # Get all active articles of the same type, excluding current article
        candidate_articles = (
            HighlightsAndEditorials.objects.filter(is_active=True, type=self.type)
            .exclude(id=self.id)
            .order_by("-created_at")
        )

        if not candidate_articles.exists():
            return HighlightsAndEditorials.objects.none()

        # Calculate similarity scores efficiently
        related_articles = []
        current_tags = set(self.tag_list)

        # Process articles in batches to avoid memory issues
        for article in candidate_articles.iterator(chunk_size=50):
            if not article.tags:  # Skip articles without tags
                continue

            article_tags = set(article.tag_list)

            # Calculate Jaccard similarity (intersection over union)
            intersection = len(current_tags.intersection(article_tags))
            union = len(current_tags.union(article_tags))

            if union == 0:
                continue

            similarity = intersection / union

            if similarity >= threshold:
                related_articles.append((article, similarity))

                # Early termination if we have enough high-similarity results
                if len(related_articles) >= limit * 2:
                    break

        # Sort by similarity (highest first) and return limited results
        related_articles.sort(key=lambda x: x[1], reverse=True)
        return [article for article, _ in related_articles[:limit]]
