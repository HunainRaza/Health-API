from django.urls import path, include
from . import views

urlpatterns = [
    # Authentication endpoints
    path('auth/register/', views.UserRegistrationView.as_view(), name='register'),
    path('auth/login/', views.CustomAuthToken.as_view(), name='login'),
    path('auth/logout/', views.logout_view, name='logout'),
    path('auth/refresh-token/', views.refresh_token_view, name='refresh_token'),
    path('auth/', include('dj_rest_auth.urls')),
    
    # Profile endpoints
    path('profile/', views.user_profile_view, name='user_profile'),
    path('profile/patient/', views.PatientProfileView.as_view(), name='patient_profile'),
    path('profile/doctor/', views.DoctorProfileView.as_view(), name='doctor_profile'),
    
    # Doctor and Patient listings
    path('doctors/', views.DoctorListView.as_view(), name='doctor_list'),
    path('patients/', views.PatientListView.as_view(), name='patient_list'),
    
    # Doctor-Patient assignments
    path('assignments/', views.DoctorPatientAssignmentListView.as_view(), name='assignment_list'),
    path('assignments/create/', views.AssignDoctorToPatientView.as_view(), name='create_assignment'),
    path('assignments/<int:assignment_id>/deactivate/', views.deactivate_assignment_view, name='deactivate_assignment'),
]
