"""Models for the Publications page."""

from django.db import models


class PublicationPathogens(models.Model):
    """Model to save pathogens list for which recent publications are fetched.

    Attributes:
        name: Name of the pathogen.
        query_string: Query string used to fetch publications related to the pathogen.
        is_active: Boolean indicating if the pathogen is active for fetching publications.
        created_at: Timestamp when the pathogen entry was created.
        updated_at: Timestamp when the pathogen entry was last updated.

    Example:
        Create a new pathogen entry:

        .. code-block:: python

            pathogen = PublicationPathogens.objects.create(
                name="Influenza",
                query_string='ABSTRACT:"Influenza"',
                is_active=True
            )
    """

    # Fields
    name = models.CharField(max_length=255, help_text="Name of the pathogen")
    query_string = models.CharField(
        max_length=500, help_text="Query string used to fetch publications related to the pathogen"
    )
    # Status field
    is_active = models.BooleanField(
        default=True, help_text="Whether this pathogen is active and used for fetching publications"
    )
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Meta class for PublicationPathogens model."""

        verbose_name = "Publications Pathogen"
        verbose_name_plural = "Publications Pathogens"

    def __str__(self) -> str:
        """Return the pathogen name for string representation."""
        return self.name
