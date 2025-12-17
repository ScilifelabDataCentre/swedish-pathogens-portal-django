from utils.views import BaseTemplateView, BaseDetailView

from .models import PlpProject


class PlpProgram(BaseTemplateView):
    template_name = "plp/index.html"
    title = "Pandemic Laboratory Preparedness Program"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["projects"] = PlpProject.objects.filter(is_active=True).order_by("-created_at")
        return context


class PlpProjectDetail(BaseDetailView):
    template_name = "plp/project_detail.html"
    model = PlpProject
    context_object_name = "project"
