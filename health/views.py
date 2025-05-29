from rest_framework import generics, status, filters, serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework.backends import DjangoFilterBackend
from django.db.models import Q
from django.shortcuts import get_object_or_404

from .models import HealthRecord, DoctorAnnotation
from .serializers import (
    HealthRecordSerializer, 
    DoctorAnnotationSerializer, 
    HealthRecordListSerializer,
)
from users.permissions import IsPatient, IsDoctor, IsOwnerOrAssignedDoctor
from users.models import Patient, DoctorPatientAssignment
# from notifications.utils import send_assignment_notification


class HealthRecordListCreateView(generics.ListCreateAPIView):
    """List and create health records"""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['record_type', 'priority', 'date_of_record']
    search_fields = ['title', 'description', 'symptoms']
    ordering_fields = ['date_of_record', 'created', 'priority']
    ordering = ['-date_of_record']

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return HealthRecordListSerializer
        return HealthRecordSerializer

    def get_queryset(self):
        user = self.request.user
        
        if user.user_type == 'patient':
            # Patients can see all their records
            return HealthRecord.objects.filter(patient=user.patient_profile)
        
        elif user.user_type == 'doctor':
            # Doctors can see records of assigned patients only
            assigned_patients = Patient.objects.filter(
                doctor_assignments__doctor=user.doctor_profile,
                doctor_assignments__is_active=True
            )
            return HealthRecord.objects.filter(
                patient__in=assigned_patients,
                is_private=False  # Doctors can't see private records
            )
        
        return HealthRecord.objects.none()

    def perform_create(self, serializer):
        # Only patients can create records
        if self.request.user.user_type != 'patient':
            raise serializers.ValidationError("Only patients can create health records.")
        serializer.save()


class HealthRecordDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a health record"""
    serializer_class = HealthRecordSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAssignedDoctor]

    def get_queryset(self):
        user = self.request.user
        
        if user.user_type == 'patient':
            return HealthRecord.objects.filter(patient=user.patient_profile)
        
        elif user.user_type == 'doctor':
            assigned_patients = Patient.objects.filter(
                doctor_assignments__doctor=user.doctor_profile,
                doctor_assignments__is_active=True
            )
            return HealthRecord.objects.filter(
                patient__in=assigned_patients,
                is_private=False
            )
        
        return HealthRecord.objects.none()

    def update(self, request, *args, **kwargs):
        # Only patients can update their records
        if request.user.user_type != 'patient':
            return Response(
                {"detail": "Only patients can update health records."}, 
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        # Only patients can delete their records
        if request.user.user_type != 'patient':
            return Response(
                {"detail": "Only patients can delete health records."}, 
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)

class DoctorAnnotationListCreateView(generics.ListCreateAPIView):
    """List and create doctor annotations for a health record"""
    serializer_class = DoctorAnnotationSerializer
    permission_classes = [IsAuthenticated, IsDoctor]

    def get_queryset(self):
        record_id = self.kwargs.get('record_id')
        health_record = get_object_or_404(HealthRecord, id=record_id)
        if self.request.user.user_type == 'doctor':
            if not health_record.patient.doctor_assignments.filter(
                doctor=self.request.user.doctor_profile, is_active=True).exists():
                return DoctorAnnotation.objects.none()
        return DoctorAnnotation.objects.filter(health_record_id=record_id)

    def perform_create(self, serializer):
        record_id = self.kwargs.get('record_id')
        health_record = get_object_or_404(HealthRecord, id=record_id)
        # Verify doctor has access to this record
        if not health_record.patient.doctor_assignments.filter(
            doctor=self.request.user.doctor_profile, is_active=True).exists():
            raise serializers.ValidationError("You don't have access to this patient's records.")
        
        serializer.save(health_record=health_record)

class DoctorAnnotationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a doctor annotation"""
    serializer_class = DoctorAnnotationSerializer
    permission_classes = [IsAuthenticated, IsDoctor]

    def get_queryset(self):
        if self.request.user.user_type == 'doctor':
            return DoctorAnnotation.objects.filter(doctor=self.request.user.doctor_profile)
        return DoctorAnnotation.objects.none()

# class MedicalAlertListCreateView(generics.ListCreateAPIView):
#     """List and create medical alerts"""
#     serializer_class = MedicalAlertSerializer
#     permission_classes = [IsAuthenticated]
#     filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
#     filterset_fields = ['alert_type', 'severity', 'is_active']
#     search_fields = ['title', 'description']
#     ordering_fields = ['created', 'severity']
#     ordering = ['-created']

#     def get_queryset(self):
#         user = self.request.user
        
#         if user.user_type == 'patient':
#             return MedicalAlert.objects.filter(patient=user.patient_profile)
        
#         elif user.user_type == 'doctor':
#             # Doctors can see alerts of assigned patients
#             assigned_patients = Patient.objects.filter(
#                 doctor_assignments__doctor=user.doctor_profile,
#                 doctor_assignments__is_active=True
#             )
#             return MedicalAlert.objects.filter(patient__in=assigned_patients)
        
#         return MedicalAlert.objects.none()

#     def perform_create(self, serializer):
#         # Only patients can create their own alerts
#         if self.request.user.user_type != 'patient':
#             raise serializers.ValidationError("Only patients can create medical alerts.")
#         serializer.save(patient=self.request.user.patient_profile)


# class MedicalAlertDetailView(generics.RetrieveUpdateDestroyAPIView):
#     """Retrieve, update, or delete a medical alert"""
#     serializer_class = MedicalAlertSerializer
#     permission_classes = [IsAuthenticated, IsOwnerOrAssignedDoctor]

#     def get_queryset(self):
#         user = self.request.user
        
#         if user.user_type == 'patient':
#             return MedicalAlert.objects.filter(patient=user.patient_profile)
        
#         elif user.user_type == 'doctor':
#             assigned_patients = Patient.objects.filter(
#                 doctor_assignments__doctor=user.doctor_profile,
#                 doctor_assignments__is_active=True
#             )
#             return MedicalAlert.objects.filter(patient__in=assigned_patients)
        
#         return MedicalAlert.objects.none()

#     def update(self, request, *args, **kwargs):
#         # Only patients can update their alerts
#         if request.user.user_type != 'patient':
#             return Response(
#                 {"detail": "Only patients can update medical alerts."}, 
#                 status=status.HTTP_403_FORBIDDEN
#             )
#         return super().update(request, *args, **kwargs)

#     def destroy(self, request, *args, **kwargs):
#         # Only patients can delete their alerts
#         if request.user.user_type != 'patient':
#             return Response(
#                 {"detail": "Only patients can delete medical alerts."}, 
#                 status=status.HTTP_403_FORBIDDEN
#             )
#         return super().destroy(request, *args, **kwargs)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def health_summary_view(request):
    """Get health summary for the authenticated user"""
    user = request.user
    
    if user.user_type == 'patient':
        patient = user.patient_profile
        total_records = HealthRecord.objects.filter(patient=patient).count()
        recent_records = HealthRecord.objects.filter(patient=patient).order_by('-date_of_record')[:5]
        # active_alerts = MedicalAlert.objects.filter(patient=patient, is_active=True).count()
        
        return Response({
            'total_records': total_records,
            'recent_records': HealthRecordListSerializer(recent_records, many=True).data,
            # 'active_alerts': active_alerts,
            'assigned_doctors': patient.doctor_assignments.filter(is_active=True).count(),
        })
    
    elif user.user_type == 'doctor':
        doctor = user.doctor_profile
        assigned_patients_count = Patient.objects.filter(
            doctor_assignments__doctor=doctor,
            doctor_assignments__is_active=True
        ).count()
        
        total_annotations = DoctorAnnotation.objects.filter(doctor=doctor).count()
        
        return Response({
            'assigned_patients': assigned_patients_count,
            'total_annotations': total_annotations,
            'specialization': doctor.specialization,
            'years_of_experience': doctor.years_of_experience,
        })
    
    return Response({'error': 'Invalid user type'}, status=status.HTTP_400_BAD_REQUEST)
