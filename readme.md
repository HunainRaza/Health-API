# Health Record API

A secure Django REST API for managing personal health records with role-based access for patients and doctors.

## Features

- **User Authentication**: Token-based authentication with 5-minute token expiry
- **Role-based Access**: Separate functionality for patients and doctors
- **Health Records**: Patients can create, update, and manage their health records
- **Doctor Annotations**: Doctors can view and annotate assigned patient records
- **Assignment System**: Doctors can be assigned to patients with automatic notifications
- **Secure Access Control**: Strict permissions to protect sensitive health data

## Tech Stack

- **Backend**: Django 5.1, Django REST Framework
- **Database**: PostgreSQL (Supabase for production)
- **Authentication**: Token-based with custom expiry middleware
- **Deployment**: Render (production)

## Quick Start

### Prerequisites

- Python 3.8+
- PostgreSQL
- Git

### Local Development Setup

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/health-record-api.git
cd health-record-api
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r dev-requirements.txt
```

4. **Environment Configuration**
Create a `dev.env` file in the project root:
```env
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432
SECRET_KEY=your-secret-key-here
DEFAULT_FROM_EMAIL=your-email@example.com
```

5. **Database Setup**
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

6. **Run Development Server**
```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000/api/`

## API Endpoints

### Authentication
- `POST /api/users/auth/register/` - User registration
- `POST /api/users/auth/login/` - User login
- `POST /api/users/auth/logout/` - User logout
- `POST /api/users/auth/refresh-token/` - Refresh token

### User Profiles
- `GET /api/users/profile/` - Get user profile
- `GET/PUT /api/users/profile/patient/` - Patient profile
- `GET/PUT /api/users/profile/doctor/` - Doctor profile

### Health Records
- `GET/POST /api/health/` - List/Create health records
- `GET/PUT/DELETE /api/health/{id}/` - Health record details
- `GET/POST /api/health/{id}/annotations/` - Doctor annotations

### Assignments
- `GET /api/users/assignments/` - List assignments
- `POST /api/users/assignments/create/` - Create assignment
- `POST /api/users/assignments/{id}/deactivate/` - Deactivate assignment

## User Types

### Patient Features
- Register and manage profile
- Create and update health records
- View assigned doctors
- Mark records as private

### Doctor Features
- Register with professional credentials
- View assigned patient records
- Add annotations to patient records
- Receive notifications for new assignments

## Deployment

### Render Deployment

1. **Prepare for Production**
```bash
# Update prod.py with your Supabase credentials
# Set environment variables in Render dashboard
```

2. **Environment Variables for Render**
```
DJANGO_SETTINGS_MODULE=core.settings.prod
SECRET_KEY=your-production-secret-key
SUPABASE_DB_NAME=your-supabase-db-name
SUPABASE_DB_USER=your-supabase-db-user
SUPABASE_DB_PASSWORD=your-supabase-db-password
SUPABASE_DB_HOST=your-supabase-db-host
SUPABASE_DB_PORT=5432
FRONTEND_URL=your-frontend-url
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

3. **Build Command for Render**
```bash
pip install -r dev-requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
```

4. **Start Command for Render**
```bash
gunicorn core.wsgi:application
```

## Project Structure

```
health-record-api/
├── core/                   # Project configuration
│   ├── settings/
│   │   ├── common.py      # Base settings
│   │   ├── dev.py         # Development settings
│   │   └── prod.py        # Production settings
│   ├── urls.py
│   └── wsgi.py
├── users/                  # User management app
│   ├── models.py          # User, Patient, Doctor models
│   ├── serializers.py     # API serializers
│   ├── views.py           # API views
│   ├── permissions.py     # Custom permissions
│   └── middleware.py      # Token expiry middleware
├── health/                 # Health records app
│   ├── models.py          # HealthRecord, DoctorAnnotation
│   ├── serializers.py     # Health record serializers
│   ├── views.py           # Health record views
│   ├── signals.py         # Notification signals
│   └── notifications.py   # Email notifications
└── manage.py
```

## Security Features

- Token-based authentication with 5-minute expiry
- Role-based permissions (Patient/Doctor)
- HTTPS enforcement in production
- CORS configuration
- SQL injection protection via Django ORM
- XSS protection headers

## Testing

```bash
python manage.py test
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For questions or support, please open an issue on GitHub.
