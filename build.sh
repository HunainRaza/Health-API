#!/bin/bash

# Health Record API Build Script for Render
set -o errexit  # Exit on any error

echo "🏥 Starting Health Record API Build Process..."

# Install requirements
echo "📦 Installing Python requirements..."
pip install -r requirements.txt

# Show current migration status
echo "📊 Current migration status:"
python manage.py showmigrations --settings=core.settings.prod

# Create migrations for custom apps only
echo "🔧 Creating migrations for custom apps..."
python manage.py makemigrations users --settings=core.settings.prod || true
python manage.py makemigrations health --settings=core.settings.prod || true

# Apply ALL migrations using fake-initial to handle existing tables
echo "⚙️  Applying all migrations with fake-initial..."
python manage.py migrate --fake-initial --settings=core.settings.prod

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput --settings=core.settings.prod

# Create superuser if environment variables are provided
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ] && [ -n "$DJANGO_SUPERUSER_EMAIL" ]; then
    python manage.py createsuperuser --settings=core.settings.prod
  echo "Super User created successfully!"
fi

# Verify final migration status
echo "✅ Final migration status:"
python manage.py showmigrations --settings=core.settings.prod

# Test database connection
echo "🔌 Testing database connection..."
python manage.py shell --settings=core.settings.prod << EOF
from django.db import connection
try:
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1;")
        print("✅ Database connection successful!")
except Exception as e:
    print(f"❌ Database connection failed: {e}")
    exit(1)
EOF

echo "🎉 Build completed successfully!"
echo "🚀 Health Record API is ready for deployment!"