from django.contrib import admin
from .models import Doctor, Patient

# Register your models here.

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('user', 'specialization', 'created', 'modified')
    search_fields = ('user__username', 'specialization')
    list_filter = ('specialization', 'created', 'modified')
    ordering = ('-created',)

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('user', 'created', 'modified')
    search_fields = ('user__username',)
    list_filter = ('created', 'modified')
    ordering = ('-created',)
