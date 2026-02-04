"""Breadcrumbs utility for generating navigation breadcrumbs.

This module provides functionality to automatically generate breadcrumb
navigation based on the current URL path. Breadcrumbs help users understand
their location within the site hierarchy and provide quick navigation.

Example:
    Generate breadcrumbs for a request:

    .. code-block:: python

        from utils.breadcrumbs import get_breadcrumbs

        breadcrumbs = get_breadcrumbs(request)
        # Returns: [BreadcrumbItem(name="Home", url="/", is_active=False),
        #           BreadcrumbItem(name="Topics", url="/topics/", is_active=False),
        #           BreadcrumbItem(name="COVID-19", url="/topics/covid-19/", is_active=True)]
"""

from dataclasses import dataclass
from typing import Optional

from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.http import Http404, HttpRequest
from django.urls import NoReverseMatch, resolve, reverse
from django.urls.exceptions import Resolver404
from django.views.generic import DetailView

from utils.breadcrumb_names import BREADCRUMB_NAME_MAPPING


@dataclass
class BreadcrumbItem:
    """Represents a single breadcrumb item in the navigation trail.

    Attributes:
        name (str): Display name for the breadcrumb link.
        url (str): URL path for the breadcrumb link.
        is_active (bool): Whether this is the current page (last item in trail).
            Defaults to False.

    Example:
        Create a breadcrumb item:

        .. code-block:: python

            item = BreadcrumbItem(
                name="Topics",
                url="/topics/",
                is_active=False
            )
    """

    name: str
    url: str
    is_active: bool = False


def get_breadcrumbs(request: HttpRequest) -> list[BreadcrumbItem]:
    """Generate breadcrumbs based on current request.

    Analyzes the current URL path and generates appropriate breadcrumb
    items. Always includes home as first item (except on homepage).
    Automatically handles nested paths and URL names.

    The function:
    - Returns empty list for homepage
    - Parses URL path segments to build breadcrumb trail
    - Resolves URL names to get display names
    - Handles namespaced URLs (e.g., "topics:index")
    - Marks the last item as active

    Args:
        request: The current HTTP request object containing path information.

    Returns:
        List of BreadcrumbItem objects representing the breadcrumb trail.
        Empty list for homepage.

    Example:
        For URL "/topics/covid-19/":

        .. code-block:: python

            breadcrumbs = get_breadcrumbs(request)
            # Returns:
            # [
            #     BreadcrumbItem(name="Home", url="/", is_active=False),
            #     BreadcrumbItem(name="Topics", url="/topics/", is_active=False),
            #     BreadcrumbItem(name="COVID-19", url="/topics/covid-19/", is_active=True)
            # ]
    """
    path = request.path

    # Homepage should not have breadcrumbs
    if path == "/":
        try:
            resolved = resolve(path)
            if resolved.url_name == "index" and resolved.namespace == "home":
                return []
        except Resolver404:
            pass

    breadcrumbs_list: list[BreadcrumbItem] = []

    # Always start with Home (except on homepage, which we already handled)
    try:
        home_url = reverse("home:index")
        breadcrumbs_list.append(
            BreadcrumbItem(name="Home", url=home_url, is_active=False)
        )
    except NoReverseMatch:
        # Fallback if home URL can't be resolved
        breadcrumbs_list.append(BreadcrumbItem(name="Home", url="/", is_active=False))

    # Parse path segments
    path_segments = [seg for seg in path.split("/") if seg]

    if not path_segments:
        # If no segments after home, we're done
        return breadcrumbs_list

    # Build breadcrumbs for each path segment
    current_path = ""
    for i, segment in enumerate(path_segments):
        current_path += f"/{segment}"

        # Try to resolve the URL to get better name and correct URL
        try:
            resolved = resolve(current_path)
            # For the last segment (current page), try to get object name if it's a detail view
            is_active = i == len(path_segments) - 1
            if is_active:
                name = _get_breadcrumb_name(resolved, segment, request)
            else:
                name = _get_breadcrumb_name(resolved, segment, None)
            # Try to reverse the URL to get the canonical URL
            try:
                full_url_name = (
                    f"{resolved.namespace}:{resolved.url_name}"
                    if resolved.namespace
                    else resolved.url_name
                )
                url = reverse(full_url_name, args=resolved.args, kwargs=resolved.kwargs)
            except (NoReverseMatch, KeyError):
                # Fallback to constructed path with trailing slash for list views
                url = current_path + "/"
        except Resolver404:
            # If can't resolve, use segment as name
            name = _format_segment_name(segment)
            # For unresolved paths, preserve original path structure
            # Add trailing slash for intermediate segments, use original for last
            if i < len(path_segments) - 1:
                url = current_path + "/"
            else:
                # Use original path to preserve trailing slash if present
                url = path if path.endswith("/") else current_path
            is_active = i == len(path_segments) - 1

        breadcrumbs_list.append(
            BreadcrumbItem(name=name, url=url, is_active=is_active)
        )

    return breadcrumbs_list


def _get_breadcrumb_name(resolved, segment: str, request: Optional[HttpRequest] = None) -> str:
    """Get display name for breadcrumb from resolved URL.

    Attempts to get a meaningful display name from the resolved URL using
    the following priority:
    1. URL name mapping (if available and not None)
    2. Object name for detail views (if request provided and object available)
    3. App namespace formatted as display name
    4. Formatted path segment

    Args:
        resolved: Resolved URL object from Django's resolve().
        segment: The URL path segment.
        request: Optional HTTP request object. Required to extract object
            names from detail views for the current page.

    Returns:
        Display name for the breadcrumb.

    Example:
        For "topics:index" -> "Topics"
        For "topics:topic_detail" with request -> "COVID-19" (object name)
        For "dashboards:lineage_competition" -> "Lineage Competition"
    """
    # Try to get name from URL name
    url_name = resolved.url_name
    namespace = resolved.namespace

    # Build full URL name with namespace if available
    full_url_name = f"{namespace}:{url_name}" if namespace else url_name

    # Check if we have a mapping for this URL name
    if full_url_name in BREADCRUMB_NAME_MAPPING:
        mapped_name = BREADCRUMB_NAME_MAPPING[full_url_name]
        # If mapping explicitly returns None, it's a detail view (use object name)
        if mapped_name is None:
            # Try to get object name from view if request is available (current page)
            if request is not None:
                object_name = _get_object_name_from_view(resolved, request)
                if object_name:
                    return object_name
            # Fallback to formatted segment if object not available
            return _format_segment_name(segment)
        # If mapping returns a string, use it
        return mapped_name

    # Use app namespace as name if available
    if namespace:
        return _format_app_name(namespace)

    # Fallback to formatted segment
    return _format_segment_name(segment)


def _format_segment_name(segment: str) -> str:
    """Format URL segment into readable display name.

    Converts URL segments (e.g., "data-management") into readable
    names (e.g., "Data Management").

    Args:
        segment: URL path segment.

    Returns:
        Formatted display name.
    """
    # Replace hyphens with spaces and capitalize words
    return segment.replace("-", " ").replace("_", " ").title()


def _format_app_name(namespace: str) -> str:
    """Format app namespace into readable display name.

    Converts app namespace (e.g., "data_management") into readable
    name (e.g., "Data Management").

    Args:
        namespace: App namespace.

    Returns:
        Formatted display name.
    """
    return namespace.replace("_", " ").title()


def _get_object_name_from_view(resolved, request: HttpRequest) -> Optional[str]:
    """Extract object name from detail view for the current page breadcrumb.

    We instantiate the view and call get_object() so we reuse the view's
    queryset and lookup logic (e.g. is_active, slug) instead of
    duplicating it here. Caller falls back to formatted segment if this
    returns None.

    Args:
        resolved: Resolved URL object from Django's resolve().
        request: The current HTTP request object.

    Returns:
        Object name string if available, None otherwise.
    """
    view_class = resolved.func

    if not isinstance(view_class, type) or not issubclass(view_class, DetailView):
        return None

    try:
        view = view_class()
        if hasattr(view, "setup"):
            view.setup(request, *resolved.args, **resolved.kwargs)
        else:
            view.request = request
            view.args = resolved.args
            view.kwargs = resolved.kwargs

        if hasattr(view, "get_object"):
            obj = view.get_object()
            if obj:
                return str(obj)
    except (Http404, PermissionDenied, ObjectDoesNotExist):
        # Object not found, no permission, or filtered out (e.g. is_active=False).
        return None

    return None
