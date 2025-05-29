from rest_framework import serializers
from django.contrib.auth import authenticate
from django.db import transaction
from dj_rest_auth.registration.serializers import RegisterSerializer
from dj_rest_auth.serializers import TokenSerializer, LoginSerializer
from rest_framework.authtoken.models import Token
from .models import User, Patient, Doctor, DoctorPatientAssignment


class UserRegisterSerializer(RegisterSerializer):
    user_type = serializers.ChoiceField(choices=User.USER_TYPE_CHOICES, required=True)
    first_name = serializers.CharField(max_length=30, required=True)
    last_name = serializers.CharField(max_length=30, required=True)
    phone = serializers.CharField(max_length=17, required=False)
    
    # Patient specific fields
    date_of_birth = serializers.DateField(required=False)
    blood_type = serializers.CharField(max_length=5, required=False)
    emergency_contact_name = serializers.CharField(max_length=100, required=False)
    emergency_contact_phone = serializers.CharField(max_length=17, required=False)
    medical_history = serializers.CharField(required=False)
    
    # Doctor specific fields
    license_number = serializers.CharField(max_length=50, required=False)
    specialization = serializers.CharField(max_length=100, required=False)
    years_of_experience = serializers.IntegerField(required=False)
    hospital_affiliation = serializers.CharField(max_length=200, required=False)
    
    username = None
    password2 = None

    def validate(self, attrs):
        user_type = attrs.get('user_type')
        
        if user_type == 'patient':
            required_fields = ['date_of_birth', 'emergency_contact_name', 'emergency_contact_phone']
            for field in required_fields:
                if not attrs.get(field):
                    raise serializers.ValidationError(f"{field} is required for patients.")
        
        elif user_type == 'doctor':
            required_fields = ['license_number', 'specialization', 'years_of_experience']
            for field in required_fields:
                if not attrs.get(field):
                    raise serializers.ValidationError(f"{field} is required for doctors.")
        
        return attrs

    @transaction.atomic
    def save(self, request):
        user = super().save(request)
        user.user_type = self.validated_data.get('user_type')
        user.first_name = self.validated_data.get('first_name')
        user.last_name = self.validated_data.get('last_name')
        user.phone = self.validated_data.get('phone', '')
        user.save()
        
        if user.user_type == 'patient':
            Patient.objects.create(
                user=user,
                date_of_birth=self.validated_data.get('date_of_birth'),
                blood_type=self.validated_data.get('blood_type', ''),
                emergency_contact_name=self.validated_data.get('emergency_contact_name'),
                emergency_contact_phone=self.validated_data.get('emergency_contact_phone'),
                medical_history=self.validated_data.get('medical_history', '')
            )
        
        elif user.user_type == 'doctor':
            Doctor.objects.create(
                user=user,
                license_number=self.validated_data.get('license_number'),
                specialization=self.validated_data.get('specialization'),
                years_of_experience=self.validated_data.get('years_of_experience'),
                hospital_affiliation=self.validated_data.get('hospital_affiliation', '')
            )
        
        return user


class UserTokenSerializer(TokenSerializer):
    user_type = serializers.SerializerMethodField()
    user_id = serializers.SerializerMethodField()
    profile_id = serializers.SerializerMethodField()

    class Meta:
        model = Token
        fields = ('key', 'user_type', 'user_id', 'profile_id')

    def get_user_type(self, obj):
        return obj.user.user_type

    def get_user_id(self, obj):
        return obj.user.id

    def get_profile_id(self, obj):
        if obj.user.user_type == 'patient' and hasattr(obj.user, 'patient_profile'):
            return obj.user.patient_profile.id
        elif obj.user.user_type == 'doctor' and hasattr(obj.user, 'doctor_profile'):
            return obj.user.doctor_profile.id
        return None

class UserLoginSerializer(LoginSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(style={'input_type': 'password'})
    username = None
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(
                request=self.context.get('request'),
                username=email,  # Using email as username
                password=password
            )
            
            if not user:
                raise serializers.ValidationError('Invalid email or password.')
            
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled.')
            
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError('Must include "email" and "password".')

    def authenticate(self, **kwargs):
        return authenticate(self.context['request'], username=kwargs['email'], password=kwargs['password'])


class PatientSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    full_name = serializers.CharField(source='user.full_name', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Patient
        fields = '__all__'


class DoctorSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    full_name = serializers.CharField(source='user.full_name', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Doctor
        fields = '__all__'


class DoctorPatientAssignmentSerializer(serializers.ModelSerializer):
    doctor_name = serializers.CharField(source='doctor.user.full_name', read_only=True)
    patient_name = serializers.CharField(source='patient.user.full_name', read_only=True)
    assigned_by_name = serializers.CharField(source='assigned_by.full_name', read_only=True)

    class Meta:
        model = DoctorPatientAssignment
        fields = '__all__'
