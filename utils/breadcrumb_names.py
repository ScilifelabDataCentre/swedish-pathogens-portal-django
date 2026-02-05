"""URL name → breadcrumb display name mapping.

Keys are full URL names (e.g. "app:view_name"); values are the label string
or None for detail views (breadcrumb utility uses the object's name instead).
"""

# URL name → display name, or None for detail views
BREADCRUMB_NAME_MAPPING: dict[str, str | None] = {
    # Home
    "home:index": "Home",
    # Topics
    "topics:index": "Topics",
    "topics:topic_detail": None,  # detail: use object name
    # Articles
    "articles:index": "Articles",
    "articles:detail": None,  # detail: use object name
    # Dashboards
    "dashboards:index": "Data dashboards",
    "dashboards:lineage_competition": "SARS-CoV-2 Variant Competition",
    "dashboards:multidisease_serology": "Multi-disease serology",
    "dashboards:serology_statistics": (
        "SARS-CoV-2 serology tests by the SciLifeLab Autoimmunity and Serology Profiling unit"
    ),
    "dashboards:variants_region_uppsala": "SARS-CoV-2 variants detected in Region Uppsala",
    "dashboards:historic_covid_publications": "Swedish COVID-19 publications over 5 years",
    "dashboards:historic_covid_quantification_gu": "Amount of SARS-CoV-2 in wastewater (GU)",
    "dashboards:covid_quantification_kth": "Amount of SARS-CoV-2 in wastewater (SEEC-KTH)",
    "dashboards:crush_covid": "CRUSH Covid data and dashboard, Region Uppsala",
    "dashboards:historic_enteric_quantification_gu": "Amount of enteric virus in wastewater (GU)",
    "dashboards:historic_sarscov2_wastewater": "Historic SARS-CoV-2 wastewater data (SEEC-SLU)",
    "dashboards:historic_influenza": "Historic data of influenza virus in wastewater (SLU)",
    "dashboards:npc_statistics": ("National Pandemic Centre SARS-CoV-2 (COVID-19) test statistics"),
    "dashboards:post_covid": "Post COVID-19 condition in Sweden: statistics and available data",
    "dashboards:recovac": "Register-based COVID-19 vaccination study (RECOVAC)",
    "dashboards:symptom_study_sweden": "COVID Symptom Study Sweden",
    "dashboards:vaccines": "The Administration and Study of COVID-19 Vaccines in Sweden",
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
