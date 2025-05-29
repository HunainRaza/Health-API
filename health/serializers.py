from rest_framework import serializers
from .models import HealthRecord, DoctorAnnotation


class HealthRecordSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.user.full_name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    last_updated_by_name = serializers.CharField(source='last_updated_by.full_name', read_only=True)
    doctor_annotations = serializers.SerializerMethodField()

    class Meta:
        model = HealthRecord
        fields = '__all__'
        read_only_fields = ('patient', 'created_by', 'last_updated_by')

    def get_doctor_annotations(self, obj):
        # Only show annotations if user is the patient or an assigned doctor
        request = self.context.get('request')
        if request and request.user:
            if (request.user.user_type == 'patient' and obj.patient.user == request.user) or \
               (request.user.user_type == 'doctor' and 
                obj.patient.doctor_assignments.filter(
                    doctor=request.user.doctor_profile, is_active=True).exists()):
                return DoctorAnnotationSerializer(obj.doctor_annotations.all(), many=True).data
        return []

    def create(self, validated_data):
        # Set patient from request user
        request = self.context.get('request')
        if request and request.user.user_type == 'patient':
            validated_data['patient'] = request.user.patient_profile
            validated_data['created_by'] = request.user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        request = self.context.get('request')
        if request:
            validated_data['last_updated_by'] = request.user
        return super().update(instance, validated_data)


class DoctorAnnotationSerializer(serializers.ModelSerializer):
    doctor_name = serializers.CharField(source='doctor.user.full_name', read_only=True)
    doctor_specialization = serializers.CharField(source='doctor.specialization', read_only=True)

    class Meta:
        model = DoctorAnnotation
        fields = '__all__'
        read_only_fields = ('doctor', 'health_record')

    def create(self, validated_data):
        request = self.context.get('request')
        if request and request.user.user_type == 'doctor':
            validated_data['doctor'] = request.user.doctor_profile
        return super().create(validated_data)


class HealthRecordListSerializer(serializers.ModelSerializer):
    """Simplified serializer for list views"""
    patient_name = serializers.CharField(source='patient.user.full_name', read_only=True)
    annotation_count = serializers.SerializerMethodField()

    class Meta:
        model = HealthRecord
        fields = ['id', 'title', 'record_type', 'date_of_record', 'priority', 
                 'patient_name', 'annotation_count', 'created', 'modified']

    def get_annotation_count(self, obj):
        return obj.doctor_annotations.count()
