"""Plotly visualization views package for dashboard pages.

This package provides view classes for dashboard pages that need to fetch
and render Plotly visualizations from external data sources.
"""

from .plotly import PlotlyDashboardView

__all__ = ["PlotlyDashboardView"]
