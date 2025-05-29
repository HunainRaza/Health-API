from rest_framework import permissions
from rest_framework.permissions import BasePermission


class IsPatient(BasePermission):
    """Allow access only to patients."""
    message = 'Access restricted to patients only.'

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            request.user.user_type == 'patient'
        )

class IsDoctor(BasePermission):
    """Allow access only to doctors."""
    message = 'Access restricted to doctors only.'

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            request.user.user_type == 'doctor' and
            hasattr(request.user, 'doctor_profile') and
            request.user.doctor_profile.is_verified
        )


class IsPatientOwner(BasePermission):
    """Allow patients to access only their own data."""
    message = 'You can only access your own records.'

    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'patient'):
            return obj.patient.user == request.user
        elif hasattr(obj, 'user'):
            return obj.user == request.user
        return False


class IsDoctorAssigned(BasePermission):
    """Allow doctors to access only assigned patients' data."""
    message = 'You can only access records of assigned patients.'

    def has_object_permission(self, request, view, obj):
        if not hasattr(request.user, 'doctor_profile'):
            return False
        
        # Check if doctor is assigned to the patient
        if hasattr(obj, 'patient'):
            return obj.patient.doctor_assignments.filter(
                doctor=request.user.doctor_profile,
                is_active=True
            ).exists()
        return False


class IsOwnerOrAssignedDoctor(BasePermission):
    """Allow patients to access their own data or assigned doctors to access patient data."""
    message = 'Access denied.'

    def has_object_permission(self, request, view, obj):
        # Patient accessing their own data
        if request.user.user_type == 'patient':
            if hasattr(obj, 'patient'):
                return obj.patient.user == request.user
            elif hasattr(obj, 'user'):
                return obj.user == request.user
        
        # Doctor accessing assigned patient's data
        elif request.user.user_type == 'doctor':
            if hasattr(request.user, 'doctor_profile') and request.user.doctor_profile.is_verified:
                if hasattr(obj, 'patient'):
                    return obj.patient.doctor_assignments.filter(
                        doctor=request.user.doctor_profile,
                        is_active=True
                    ).exists()
        
        return False
