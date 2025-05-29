from django.contrib import admin
from .models import HealthRecord, DoctorAnnotation

# Register your models here.

@admin.register(HealthRecord)
class HealthRecordAdmin(admin.ModelAdmin):
    list_display = ('patient', 'created', 'priority', 'description')
    search_fields = ('patient__username', 'doctor__username', 'priority', 'description')
    list_filter = ('priority', 'description', 'created')
    ordering = ('-created',)

@admin.register(DoctorAnnotation)
class DoctorAnnotationAdmin(admin.ModelAdmin):
    list_display = ('health_record', 'doctor', 'annotation', 'created')
    search_fields = ('health_record__patient__username', 'doctor__username', 'annotation')
    list_filter = ('created',)
    ordering = ('-created',)
