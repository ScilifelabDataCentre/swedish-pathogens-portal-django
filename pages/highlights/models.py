from django.db import models
from django.utils.text import slugify
from django.utils.safestring import mark_safe
from typing import List
import markdown


class DataHighlight(models.Model):
    """Data highlight model for showcasing research findings and scientific discoveries.

    Represents research highlights that showcase important scientific findings,
    data insights, and discoveries for the Swedish Pathogens Portal. Each highlight
    includes comprehensive information about research projects and can be associated
    with multiple topics for better content organization and discovery.

    Attributes:
        title (str): Display title of the highlight (max 255 chars, unique).
        slug (str): URL-friendly version of title (auto-generated from title).
        summary (str): Brief summary displayed in highlight cards.
        content (str): Full markdown content displayed on detail pages.
        announcement (str, optional): Prominent announcement message for highlights.
        tags (str, optional): Comma-separated tags for content matching and search.
        featured_image (ImageField): Primary image displayed with the highlight.
        figure_caption (str, optional): Descriptive caption for the featured image.
        topics (ManyToMany, optional): Research topics associated with this highlight.
        is_active (bool): Whether highlight is visible to users (default: True).
        created_at (datetime): Timestamp when highlight was created.
        updated_at (datetime): Timestamp when highlight was last modified.

    Example:
        Create a new data highlight:

        .. code-block:: python

            highlight = DataHighlight.objects.create(
                title="Novel Pathogen Discovery in Swedish Waters",
                summary="Researchers discovered a new bacterial species...",
                content="# Research Findings\n\nDetailed findings...",
                featured_image="pathogen_discovery.jpg"
            )
            # slug automatically generated as "novel-pathogen-discovery-in-swedish-waters"
    """
    # Required fields
    title = models.CharField(
        max_length=255,
        unique=True,
        help_text="Title of the data highlight"
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        help_text="URL-friendly version of the title (auto-generated from title)"
    )
    
    # Content fields
    summary = models.TextField(
        help_text="Brief summary of the highlight for display in cards"
    )
    content = models.TextField(
        help_text="Full content in markdown format displayed on detail page"
    )
    announcement = models.TextField(
        blank=True,
        help_text="Optional announcement message displayed at the top of the highlight"
    )
    tags = models.TextField(
        blank=True,
        help_text="Comma-separated tags for related content matching and search"
    )
    
    # Media fields
    featured_image = models.ImageField(
        upload_to="highlights/images/",
        help_text="Featured image for the highlight"
    )
    figure_caption = models.TextField(
        blank=True,
        help_text="Caption for the featured image (optional)"
    )
    
    # Relationships
    topics = models.ManyToManyField(
        "topics.Topic",
        blank=True,
        help_text="Research topics associated with this highlight (optional)"
    )
    
    # Status field
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this highlight is active and visible"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Data Highlight"
        verbose_name_plural = "Data Highlights"
    
    def __str__(self):
        """Return the highlight title for string representation."""
        return self.title
    
    def save(self, *args, **kwargs):
        """Save the highlight, auto-generating slug if not provided."""
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    @property
    def rendered_content(self):
        """Return content rendered as HTML from markdown."""
        return mark_safe(
            markdown.markdown(self.content, extensions=["extra", "codehilite"])
        )
    
    @property
    def rendered_announcement(self):
        """Return announcement rendered as HTML from markdown."""
        if self.announcement:
            return mark_safe(
                markdown.markdown(self.announcement, extensions=["extra", "codehilite"])
            )
        return ""
    
    @property
    def tag_list(self):
        """Return tags as a list of cleaned strings."""
        if not self.tags:
            return []
        return [tag.strip().lower() for tag in self.tags.split(',') if tag.strip()]
    
    def get_related_highlights(self, limit: int = 4, threshold: float = 0.1) -> List['DataHighlight']:
        """Get related highlights based on tag similarity.
        
        Finds highlights with similar tags using Jaccard similarity algorithm.
        Considers all related highlights regardless of creation date (past and future).
        Results are ordered by similarity score (highest first).
        
        Args:
            limit: Maximum number of related highlights to return (default: 4)
            threshold: Minimum similarity threshold between 0.0 and 1.0 (default: 0.1)
            
        Returns:
            List of related highlights ordered by similarity score
            
        Example:
            Get top 3 related highlights with at least 20% similarity:
            
            .. code-block:: python
                
                related = highlight.get_related_highlights(limit=3, threshold=0.2)
                for related_highlight in related:
                    print(related_highlight.title)
        """
        if not self.tag_list:
            return DataHighlight.objects.none()
        
        # Get all active highlights, excluding current highlight
        candidate_highlights = DataHighlight.objects.filter(
            is_active=True
        ).exclude(id=self.id).order_by('-created_at')
        
        if not candidate_highlights.exists():
            return DataHighlight.objects.none()
        
        # Calculate similarity scores efficiently
        related_highlights = []
        current_tags = set(self.tag_list)
        
        # Process highlights in batches to avoid memory issues
        for highlight in candidate_highlights.iterator(chunk_size=50):
            if not highlight.tags:  # Skip highlights without tags
                continue
                
            highlight_tags = set(highlight.tag_list)
            
            # Calculate Jaccard similarity (intersection over union)
            intersection = len(current_tags.intersection(highlight_tags))
            union = len(current_tags.union(highlight_tags))
            
            if union == 0:
                continue
                
            similarity = intersection / union
            
            if similarity >= threshold:
                related_highlights.append((highlight, similarity))
                
                # Early termination if we have enough high-similarity results
                if len(related_highlights) >= limit * 2:
                    break
        
        # Sort by similarity (highest first) and return limited results
        related_highlights.sort(key=lambda x: x[1], reverse=True)
        return [highlight for highlight, _ in related_highlights[:limit]]
    


