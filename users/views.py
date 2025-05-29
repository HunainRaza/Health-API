from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from django.contrib.auth import authenticate
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from django.shortcuts import get_object_or_404

from .models import User, Patient, Doctor, DoctorPatientAssignment
from .serializers import (
    UserRegisterSerializer, 
    UserLoginSerializer, 
    UserTokenSerializer,
    PatientSerializer, 
    DoctorSerializer, 
    DoctorPatientAssignmentSerializer
)
from .permissions import IsPatient, IsDoctor, IsPatientOwner, IsDoctorAssigned


class CustomAuthToken(ObtainAuthToken):
    """Custom token authentication with expiry"""
    serializer_class = UserLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        
        # Delete old token if exists
        Token.objects.filter(user=user).delete()
        
        # Create new token
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'token': token.key,
            'user_type': user.user_type,
            'user_id': user.id,
            'profile_id': getattr(user, f'{user.user_type}_profile', None).id if hasattr(user, f'{user.user_type}_profile') else None,
            'expires_in': int(settings.TOKEN_EXPIRY_TIME.total_seconds()),
            'full_name': user.full_name,
            'email': user.email
        })


class UserRegistrationView(generics.CreateAPIView):
    """User registration endpoint"""
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save(request)
        
        # Create token for the new user
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'user': {
                'id': user.id,
                'email': user.email,
                'user_type': user.user_type,
                'full_name': user.full_name,
            },
            'token': token.key,
            'expires_in': int(settings.TOKEN_EXPIRY_TIME.total_seconds()),
            'message': 'Registration successful'
        }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    """Logout endpoint - delete user token"""
    try:
        token = Token.objects.get(user=request.user)
        token.delete()
        return Response({'message': 'Successfully logged out'}, status=status.HTTP_200_OK)
    except Token.DoesNotExist:
        return Response({'message': 'Token not found'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def refresh_token_view(request):
    """Refresh token endpoint"""
    try:
        # Delete old token
        Token.objects.filter(user=request.user).delete()
        
        # Create new token
        token = Token.objects.create(user=request.user)
        
        return Response({
            'token': token.key,
            'expires_in': int(settings.TOKEN_EXPIRY_TIME.total_seconds()),
            'message': 'Token refreshed successfully'
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class PatientProfileView(generics.RetrieveUpdateAPIView):
    """Patient profile view"""
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated, IsPatient]

    def get_object(self):
        return self.request.user.patient_profile


class DoctorProfileView(generics.RetrieveUpdateAPIView):
    """Doctor profile view"""
    serializer_class = DoctorSerializer
    permission_classes = [permissions.IsAuthenticated, IsDoctor]

    def get_object(self):
        return self.request.user.doctor_profile


class DoctorListView(generics.ListAPIView):
    """List all verified doctors"""
    serializer_class = DoctorSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Doctor.objects.filter(is_verified=True)


class PatientListView(generics.ListAPIView):
    """List patients for doctors (only assigned patients)"""
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated, IsDoctor]

    def get_queryset(self):
        # Only show patients assigned to the requesting doctor
        return Patient.objects.filter(
            doctor_assignments__doctor=self.request.user.doctor_profile,
            doctor_assignments__is_active=True
        )


class DoctorPatientAssignmentListView(generics.ListAPIView):
    """List doctor-patient assignments"""
    serializer_class = DoctorPatientAssignmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        
        if user.user_type == 'patient':
            # Patients can see their assignments
            return DoctorPatientAssignment.objects.filter(
                patient=user.patient_profile,
                is_active=True
            )
        elif user.user_type == 'doctor':
            # Doctors can see their assignments
            return DoctorPatientAssignment.objects.filter(
                doctor=user.doctor_profile,
                is_active=True
            )
        
        return DoctorPatientAssignment.objects.none()


class AssignDoctorToPatientView(generics.CreateAPIView):
    """Assign a doctor to a patient (admin functionality)"""
    serializer_class = DoctorPatientAssignmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        # For demo purposes, allowing any authenticated user to create assignments
        # In production, this should be restricted to admin users or specific roles
        
        doctor_id = request.data.get('doctor')
        patient_id = request.data.get('patient')
        
        if not doctor_id or not patient_id:
            return Response({
                'error': 'Both doctor and patient IDs are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            doctor = Doctor.objects.get(id=doctor_id, is_verified=True)
            patient = Patient.objects.get(id=patient_id)
        except (Doctor.DoesNotExist, Patient.DoesNotExist):
            return Response({
                'error': 'Doctor or Patient not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check if assignment already exists
        existing_assignment = DoctorPatientAssignment.objects.filter(
            doctor=doctor,
            patient=patient,
            is_active=True
        ).first()
        
        if existing_assignment:
            return Response({
                'error': 'Doctor is already assigned to this patient'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create assignment
        assignment = DoctorPatientAssignment.objects.create(
            doctor=doctor,
            patient=patient,
            assigned_by=request.user,
            notes=request.data.get('notes', '')
        )
        
        serializer = self.get_serializer(assignment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def deactivate_assignment_view(request, assignment_id):
    """Deactivate a doctor-patient assignment"""
    try:
        assignment = get_object_or_404(DoctorPatientAssignment, id=assignment_id)
        
        # Check permissions
        user = request.user
        if user.user_type == 'patient' and assignment.patient.user != user:
            return Response({
                'error': 'Permission denied'
            }, status=status.HTTP_403_FORBIDDEN)
        elif user.user_type == 'doctor' and assignment.doctor.user != user:
            return Response({
                'error': 'Permission denied'
            }, status=status.HTTP_403_FORBIDDEN)
        
        assignment.is_active = False
        assignment.save()
        
        return Response({
            'message': 'Assignment deactivated successfully'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_profile_view(request):
    """Get current user profile information"""
    user = request.user
    profile_data = {
        'id': user.id,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'full_name': user.full_name,
        'user_type': user.user_type,
        'phone': user.phone,
        'date_joined': user.date_joined,
    }
    
    if user.user_type == 'patient' and hasattr(user, 'patient_profile'):
        profile_data['patient_profile'] = PatientSerializer(user.patient_profile).data
    elif user.user_type == 'doctor' and hasattr(user, 'doctor_profile'):
        profile_data['doctor_profile'] = DoctorSerializer(user.doctor_profile).data
    
    return Response(profile_data)


# Token validation middleware
class TokenExpiryMiddleware:
    """Middleware to check token expiry"""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if request has Authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if auth_header and auth_header.startswith('Token '):
            token_key = auth_header.split(' ')[1]
            try:
                token = Token.objects.get(key=token_key)
                # Check if token is expired (created more than TOKEN_EXPIRY_TIME ago)
                if timezone.now() - token.created > settings.TOKEN_EXPIRY_TIME:
                    token.delete()
                    # Token expired, but we'll let the view handle the authentication error
            except Token.DoesNotExist:
                pass
        
        response = self.get_response(request)
        return response
