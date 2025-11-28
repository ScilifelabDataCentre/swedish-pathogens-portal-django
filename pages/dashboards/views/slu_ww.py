from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views import View

from ..models import DashboardData
from ..visualisation.slu_ww import get_compiled_data

# TODO: The following is a temp workaround, it should be removed
# and the data sync lagic will be couple with researcher data
# upload page and related views
from django.contrib.auth.mixins import LoginRequiredMixin  # noqa: E402, F401
from core.settings.base import env


class SLUsync(LoginRequiredMixin, View):
    """To handle dashboard data update

    DEV - Initial approach, will be removed or updated when data upload
    page is done for the researchers
    """

    # Access related values
    raise_exception = True

    # Dashboard related values
    dashboard = "slu_wastewater"
    data_url = env("DASHBOARD_SLU_DATA", default="")

    def get(self, request: HttpRequest) -> HttpResponse:
        """To serve the temp data sync frontend page"""
        context = {
            "data_url": self.data_url,
        }
        return render(request, "dashboards/slu_ww/data_sync.html", context)

    def post(self, request: HttpRequest) -> HttpResponse:
        """To serve the temp data sync in the backend"""
        try:
            dashboard_data = DashboardData.objects.get(dashboard=self.dashboard)
        except DashboardData.DoesNotExist:
            dashboard_data = DashboardData(dashboard=self.dashboard)

        compiled_data = get_compiled_data(data_url=self.data_url)
        dashboard_data.data = compiled_data
        dashboard_data.save()

        return HttpResponse("<span class=''>Data synced successfully!!</span>")
