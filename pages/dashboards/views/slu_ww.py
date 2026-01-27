"""Views for SLU wastewater dashboards pages."""

import logging

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils.text import slugify
from django.views import View

from ..models import DashboardData
from ..visualisation.slu_ww import (
    get_all_sites_plot,
    get_compiled_data,
    get_quant_overview_plot,
    get_single_site_plot,
)
from ..visualisation.utils import plot_html_from_json

logger = logging.getLogger(__name__)


class SluWasteWater(View):
    """View to handle SLU dashboard pages.

    This class handles all the SLU wastewater dashboard pages i.e. all the URLs
    '/dashboards/wastewater-slu/<pages>'. The valid/available pages are defined
    in the 'pages' attribute. The defined 'get' method caters different page
    based on the 'active_page' attribute which is set appropriately to each page
    in the app's 'urls.py'.

    For adding new page(s) one should just add it to 'pages' or 'virus_pages' if
    it is a new virus page and add new logic (if required) in the 'get' method to
    cater the new page(s).

    Attributes:
        dashboard (str): Name of the dashboard that will be used for DB queries.
        virus_pages (list): List of viruses that will have its own page.
        pages (list): List of pages to be added under SLU dasboard. The above
            mentioned virus pages are added to this list.
        active_page (str): Based on this value the 'get' method returns
            appropriate content for that page. Default 'Overview'
        dashboard_data (DashboardData): A DashboardData model object, if there is
            no entry for this dashboard, it is set to None.

    """

    dashboard = "slu_wastewater"
    virus_pages = ["Influenza A virus", "Influenza B virus", "RSV", "SARS CoV-2"]
    pages = ["Overview", "Methodology"] + virus_pages
    active_page = "Overview"

    def get(self, request: HttpRequest) -> HttpResponse:
        """To handle the get request and returns the content based on 'active_page'."""
        try:
            dashboard_data = DashboardData.objects.get(dashboard=self.dashboard)
        except DashboardData.DoesNotExist:
            dashboard_data = None

        # common context for all the pages
        context = {
            "title": "Virus surveillance in wastewater from SLU-SEEC",
            "tabs": self.pages,
            "active": self.active_page,
        }

        dashboard_data = dashboard_data.data if dashboard_data is not None else {}
        raw_data = dashboard_data.get("raw_data")

        # handling overview page
        if self.active_page == "Overview":
            # to handle HTMX request for plot updates
            if request.htmx:
                request_params = dict(request.GET)
                plot_html = get_quant_overview_plot(data=raw_data, **request_params)
                return HttpResponse(plot_html)

            # content about recent data
            recent_data_info = dashboard_data.get("recent_data_info")
            if recent_data_info:
                context.update(**recent_data_info)
            else:
                context["no_recent_data_info"] = True
                logger.warning("No recent data info found for SLU wastewater dashboard.")

            # get filter input context
            filter_intput_context = dashboard_data.get("filter_input_context")
            if filter_intput_context:
                context.update(**filter_intput_context)
            else:
                context["no_filter_input_context"] = True
                logger.warning("No filter input context found for SLU wastewater dashboard.")

            # get overview quantitative plot
            if raw_data:
                context["quant_plot_html"] = get_quant_overview_plot(data=raw_data)
            else:
                logger.warning("No raw data found for SLU wastewater dashboard.")

            # get overview qualitative plot
            qual_orverview_plot = dashboard_data.get("qual_overview_plot")
            if qual_orverview_plot:
                context["qual_plot_html"] = plot_html_from_json(qual_orverview_plot)
            else:
                logger.warning("No qualitative overview plot found for SLU wastewater dashboard.")

            return render(request, "dashboards/slu_ww/overview.html", context)

        # handling methods page
        if self.active_page == "Methodology":
            site_info = dashboard_data.get("sites_info")
            if site_info:
                context["site_info"] = site_info
            else:
                context["no_site_info"] = True
                logger.warning("No site info found for SLU wastewater dashboard.")
            return render(request, "dashboards/slu_ww/methods.html", context)

        # handling individual virus pages
        if self.active_page in self.virus_pages:
            virus = self.active_page
            # to handle HTMX request for plot updates
            if request.htmx:
                request_params = dict(request.GET)
                # call appropriate function depending upon the plot type
                if request.GET.get("plot-toggle") == "all":
                    quant_plot_html = get_all_sites_plot(
                        data=raw_data, virus=virus, **request_params
                    )
                else:
                    quant_plot_html = get_single_site_plot(
                        data=raw_data, virus=virus, **request_params
                    )
                return HttpResponse(quant_plot_html)

            # get filter input context
            filter_intput_context = dashboard_data.get("filter_input_context")
            if filter_intput_context:
                context.update(**filter_intput_context)
            else:
                context["no_filter_input_context"] = True
                logger.warning("No filter input context found for SLU wastewater dashboard.")

            # get quantitative plot
            if raw_data:
                context["quant_plot_html"] = get_all_sites_plot(data=raw_data, virus=virus)
            else:
                logger.warning("No raw data found for SLU wastewater dashboard.")

            # get qualitative plot
            qual_plot = dashboard_data.get(f"qual_plot_{slugify(virus)}")
            if qual_plot:
                context["qual_plot_html"] = plot_html_from_json(qual_plot)
            else:
                logger.warning("No qualitative plot found for SLU wastewater dashboard.")

            return render(request, "dashboards/slu_ww/analysis.html", context)


# TODO: The following is a temp workaround, it should be removed
# and the data sync lagic will be couple with researcher data
# upload page and related views
from django.contrib.auth.mixins import LoginRequiredMixin  # noqa: E402, F401


class SLUsync(LoginRequiredMixin, View):
    """To handle dashboard data update.

    DEV - Initial approach, will be removed or updated when data upload
    page is done for the researchers
    """

    # Access related values
    raise_exception = True

    # Dashboard related values
    dashboard = "slu_wastewater"
    data_url = "https://blobserver.dc.scilifelab.se/blob/slu_test_data.csv"

    def get(self, request: HttpRequest) -> HttpResponse:
        """To serve the temp data sync frontend page."""
        context = {
            "data_url": self.data_url,
        }
        return render(request, "dashboards/slu_ww/data_sync.html", context)

    def post(self, request: HttpRequest) -> HttpResponse:
        """To serve the temp data sync in the backend."""
        try:
            dashboard_data = DashboardData.objects.get(dashboard=self.dashboard)
        except DashboardData.DoesNotExist:
            dashboard_data = DashboardData(dashboard=self.dashboard)

        compiled_data = get_compiled_data(data_url=self.data_url)
        dashboard_data.data = compiled_data
        dashboard_data.save()

        return HttpResponse("OK")
