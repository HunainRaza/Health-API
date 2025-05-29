from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from core.models import TimeStampedModel

class User(AbstractUser):
    USER_TYPE_CHOICES = [
        ('patient', 'Patient'),
        ('doctor', 'Doctor'),
    ]
    
    email = models.EmailField(unique=True)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f"{self.email} ({self.user_type})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

class Patient(TimeStampedModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient_profile')
    date_of_birth = models.DateField()
    blood_type = models.CharField(max_length=5, blank=True)
    emergency_contact_name = models.CharField(max_length=100)
    emergency_contact_phone = models.CharField(max_length=17)
    medical_history = models.TextField(blank=True)
    
    class Meta:
        db_table = 'patients'
        verbose_name = 'Patient'
        verbose_name_plural = 'Patients'

    def __str__(self):
        return f"Patient: {self.user.full_name}"

class Doctor(TimeStampedModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor_profile')
    license_number = models.CharField(max_length=50, unique=True)
    specialization = models.CharField(max_length=100)
    years_of_experience = models.PositiveIntegerField()
    hospital_affiliation = models.CharField(max_length=200, blank=True)
    is_verified = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'doctors'
        verbose_name = 'Doctor'
        verbose_name_plural = 'Doctors'

    def __str__(self):
        return f"Dr. {self.user.full_name} - {self.specialization}"

class DoctorPatientAssignment(TimeStampedModel):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='patient_assignments')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='doctor_assignments')
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'doctor_patient_assignments'
        unique_together = ['doctor', 'patient']
        verbose_name = 'Doctor-Patient Assignment'
        verbose_name_plural = 'Doctor-Patient Assignments'

    def __str__(self):
        return f"Dr. {self.doctor.user.full_name} -> {self.patient.user.full_name}"
