from django.urls import path
from . import views

app_name = 'health'

urlpatterns = [
    # Health Records endpoints
    path('', views.HealthRecordListCreateView.as_view(), name='health_record_list_create'),
    path('<int:pk>/', views.HealthRecordDetailView.as_view(), name='health_record_detail'),
    
    # Doctor Annotations endpoints
    path('<int:record_id>/annotations/', views.DoctorAnnotationListCreateView.as_view(), name='annotation_list_create'),
    path('annotations/<int:pk>/', views.DoctorAnnotationDetailView.as_view(), name='annotation_detail'),
    
    # Medical Alerts endpoints
    # path('alerts/', views.MedicalAlertListCreateView.as_view(), name='medical_alert_list_create'),
    # path('alerts/<int:pk>/', views.MedicalAlertDetailView.as_view(), name='medical_alert_detail'),
]