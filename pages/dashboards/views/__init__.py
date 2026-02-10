"""Public view exports for the dashboards app.

Re-exports view classes to provide a stable import surface for
URL configs and other modules.
"""

from .covid_quantification_kth import CovidQuantificationKth
from .crush_covid import CrushCovid
from .external_dashboards import ExternalDashboards
from .historic_covid_publications import HistoricCovidPublications
from .historic_covid_quantification_gu import HistoricCovidQuantificationGu
from .historic_enteric_quantification_gu import HistoricEntericQuantificationGu
from .historic_influenza import HistoricInfluenza
from .historic_sarscov2_wastewater import HistoricSarsCov2Wastewater
from .index import DashboardsIndex
from .lineage_competition import LineageCompetition
from .multidisease_serology import MultiDiseaseSerology
from .npc_statistics import NpcStatistics
from .post_covid import PostCovid
from .recovac import Recovac
from .serology_statistics import SerologyStatistics
from .slu_ww import SLUsync, SluWasteWater
from .symptom_study_sweden import SymptomStudySweden
from .vaccines import Vaccines
from .variants_region_uppsala import VariantsRegionUppsala

__all__ = [
    "CovidQuantificationKth",
    "CrushCovid",
    "DashboardsIndex",
    "ExternalDashboards",
    "HistoricCovidPublications",
    "HistoricCovidQuantificationGu",
    "HistoricEntericQuantificationGu",
    "HistoricInfluenza",
    "HistoricSarsCov2Wastewater",
    "LineageCompetition",
    "MultiDiseaseSerology",
    "NpcStatistics",
    "PostCovid",
    "Recovac",
    "SerologyStatistics",
    "SLUsync",
    "SluWasteWater",
    "SymptomStudySweden",
    "Vaccines",
    "VariantsRegionUppsala",
]
