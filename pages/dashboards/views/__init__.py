"""Public view exports for the dashboards app.

Re-exports view classes to provide a stable import surface for
URL configs and other modules.
"""

from .crush_covid import CrushCovid
from .covid_quantification_kth import CovidQuantificationKth
from .index import DashboardsIndex
from .lineage_competition import LineageCompetition
from .npc_statistics import NpcStatistics
from .post_covid import PostCovid
from .serology_statistics import SerologyStatistics
from .symptom_study_sweden import SymptomStudySweden
from .vaccines import Vaccines
from .variants_region_uppsala import VariantsRegionUppsala

__all__ = [
    "CrushCovid",
    "CovidQuantificationKth",
    "DashboardsIndex",
    "LineageCompetition",
    "NpcStatistics",
    "PostCovid",
    "SerologyStatistics",
    "SymptomStudySweden",
    "Vaccines",
    "VariantsRegionUppsala",
]
