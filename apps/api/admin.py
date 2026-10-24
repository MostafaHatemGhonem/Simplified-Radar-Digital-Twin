from django.contrib import admin
from .models import RadarConfiguration, Experiment, DetectionResult


@admin.register(RadarConfiguration)
class RadarConfigurationAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_by', 'is_public', 'created_at')
    list_filter = ('is_public', 'created_by')
    search_fields = ('name', 'description')


@admin.register(Experiment)
class ExperimentAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'configuration', 'owner', 'started_at', 'completed_at')
    list_filter = ('status', 'owner', 'configuration__name')
    search_fields = ('name', 'description')
    readonly_fields = ('started_at', 'completed_at')


@admin.register(DetectionResult)
class DetectionResultAdmin(admin.ModelAdmin):
    list_display = ('target_label', 'experiment', 'range_m', 'radial_velocity_mps', 'azimuth_deg', 'elevation_deg', 'confidence')
    list_filter = ('experiment', 'experiment__status')
    search_fields = ('target_label', 'experiment__name')