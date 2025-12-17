from django.contrib import admin

from .models import PlpProject


@admin.register(PlpProject)
class PlpProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "is_active", "created_at")
    list_filter = ("category", "is_active")
    search_fields = ("title", "summary")
    prepopulated_fields = {"slug": ("title",)}



