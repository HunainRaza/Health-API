from django.db import models
from users.models import TimeStampedModel, Patient, Doctor


class HealthRecord(TimeStampedModel):
    RECORD_TYPE_CHOICES = [
        ('general', 'General Health Record'),
        ('diagnosis', 'Diagnosis'),
        ('prescription', 'Prescription'),
        ('lab_result', 'Lab Result'),
        ('imaging', 'Medical Imaging'),
        ('surgery', 'Surgery Record'),
        ('vaccination', 'Vaccination Record'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='health_records')
    record_type = models.CharField(max_length=20, choices=RECORD_TYPE_CHOICES, default='general')
    title = models.CharField(max_length=200)
    description = models.TextField()
    date_of_record = models.DateTimeField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    is_private = models.BooleanField(default=False)  # Patient can mark records as private
    
    # Medical details
    symptoms = models.TextField(blank=True)
    vital_signs = models.JSONField(blank=True, null=True)  # Store BP, pulse, temp, etc.
    medications = models.TextField(blank=True)
    allergies = models.TextField(blank=True)
    
    # File attachments
    attachment = models.FileField(upload_to='health_records/attachments/', blank=True, null=True)
    
    # Tracking
    created_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, related_name='created_records')
    last_updated_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, related_name='updated_records')
    
    class Meta:
        db_table = 'health_records'
        ordering = ['-date_of_record']
        verbose_name = 'Health Record'
        verbose_name_plural = 'Health Records'

    def __str__(self):
        return f"{self.patient.user.full_name} - {self.title}"


class DoctorAnnotation(TimeStampedModel):
    health_record = models.ForeignKey(HealthRecord, on_delete=models.CASCADE, related_name='doctor_annotations')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='annotations')
    annotation = models.TextField()
    is_diagnosis = models.BooleanField(default=False)
    is_treatment_plan = models.BooleanField(default=False)
    is_follow_up_required = models.BooleanField(default=False)
    follow_up_date = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        db_table = 'doctor_annotations'
        ordering = ['-created']
        verbose_name = 'Doctor Annotation'
        verbose_name_plural = 'Doctor Annotations'

    def __str__(self):
        return f"Dr. {self.doctor.user.full_name} -> {self.health_record.title}"
