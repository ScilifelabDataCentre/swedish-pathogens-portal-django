"""Context processors for global template context.

This module provides context processors that make data available
to all templates automatically. Context processors are functions
that take a request and return a dictionary to be merged into
the template context.
"""

from typing import Any

from django.http import HttpRequest

from utils.breadcrumbs import get_breadcrumbs


def breadcrumbs(request: HttpRequest) -> dict[str, Any]:
    """Add breadcrumbs to template context.

    Makes breadcrumbs available to all templates automatically.
    Returns empty list for homepage, which allows templates to
    conditionally render breadcrumbs.

    Args:
        request: The current HTTP request object.

    Returns:
        Dictionary with 'breadcrumbs' key containing list of BreadcrumbItem
        objects representing the navigation trail. Empty list for homepage.

    Example:
        In a template, breadcrumbs are automatically available:

        .. code-block:: html

            {% if breadcrumbs %}
                {% for item in breadcrumbs %}
                    <a href="{{ item.url }}">{{ item.name }}</a>
                {% endfor %}
            {% endif %}
    """
    return {"breadcrumbs": get_breadcrumbs(request)}
