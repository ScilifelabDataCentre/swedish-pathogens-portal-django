"""URL name → breadcrumb display name mapping for the portal.

This module is the single source of truth for mapping URL names (e.g. from
Django's resolve()) to human-readable breadcrumb labels. Detail views use
None so the breadcrumb utility can substitute the object's name instead.

To add a new URL name:
    1. Add an entry to BREADCRUMB_NAME_MAPPING: key is the full URL name
       (e.g. "app:view_name"), value is the display string or None for
       detail views (object name will be used).
    2. No changes needed in utils.breadcrumbs; it imports BREADCRUMB_NAME_MAPPING.
"""

from typing import Optional

# URL name (namespace:name or name) → display name, or None for detail views
BREADCRUMB_NAME_MAPPING: dict[str, Optional[str]] = {
    # Home
    "home:index": "Home",
    # Topics
    "topics:index": "Topics",
    "topics:topic_detail": None,  # detail: use object name
    # Articles
    "articles:index": "Articles",
    "articles:detail": None,  # detail: use object name
    # Dashboards
    "dashboards:index": "Dashboards",
    "dashboards:lineage_competition": "Lineage Competition",
    "dashboards:multidisease_serology": "Multi-disease Serology",
    "dashboards:serology_statistics": "Serology Statistics",
    "dashboards:variants_region_uppsala": "Variants Region Uppsala",
    "dashboards:historic_covid_publications": "Historic COVID Publications",
    "dashboards:covid_quantification_kth": "COVID Quantification KTH",
    "dashboards:crush_covid": "Crush COVID",
    "dashboards:historic_sarscov2_wastewater": "Historic SARS-CoV-2 Wastewater",
    "dashboards:historic_influenza": "Historic Influenza",
    "dashboards:npc_statistics": "NPC Statistics",
    "dashboards:post_covid": "Post COVID",
    "dashboards:recovac": "RECOVAC",
    "dashboards:symptom_study_sweden": "Symptom Study Sweden",
    "dashboards:vaccines": "Vaccines",
    # News
    "news:index": "News",
    "news:detail": None,  # detail: use object name
    # Outbreaks
    "outbreaks:index": "Outbreaks",
    "outbreaks:detail": None,  # detail: use object name
    # Publications
    "publications:index": "Publications",
    # About
    "about:index": "About",
    "about:partners": "Partners",
    "about:funders": "Funders",
    "about:nodes": "Pathogens Portal Nodes",
    # Data Management
    "data_management:index": "Data Management",
    # Register Based Research
    "register_based_research:index": "Register Based Research",
    # Citation
    "citation:index": "Citation",
    # Contact
    "contact:index": "Contact",
    # Privacy
    "privacy:index": "Privacy",
}
