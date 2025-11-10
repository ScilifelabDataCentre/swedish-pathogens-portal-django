"""Public view exports for the dashboards app.

Re-exports view classes to provide a stable import surface for
URL configs and other modules.
"""

from .index import DashboardsIndex
from .lineage_competition import LineageCompetition

__all__ = [
    "DashboardsIndex",
    "LineageCompetition",
]
