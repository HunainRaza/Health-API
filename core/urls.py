"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def api_root(request):
    """API root endpoint with available endpoints"""
    return Response({
        'message': 'Health Record API - Welcome!',
        'version': '1.0',
        'endpoints': {
            'authentication': {
                'register': '/api/users/auth/register/',
                'login': '/api/users/auth/login/',
                'logout': '/api/users/auth/logout/',
                'refresh_token': '/api/users/auth/refresh-token/',
            },
            'users': {
                'profile': '/api/users/profile/',
                'patient_profile': '/api/users/profile/patient/',
                'doctor_profile': '/api/users/profile/doctor/',
                'doctors': '/api/users/doctors/',
                'patients': '/api/users/patients/',
            },
            'assignments': {
                'list': '/api/users/assignments/',
                'create': '/api/users/assignments/create/',
                'deactivate': '/api/users/assignments/{id}/deactivate/',
            },
            'health_records': {
                'list_create': '/api/health/',
                'detail': '/api/health/{id}/',
                'annotations': '/api/health/{id}/annotations/',
            },
            'admin': '/admin/',
        }
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', api_root, name='api_root'),
    path('api/users/', include('users.urls')),
    path('api/health/', include('health.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
