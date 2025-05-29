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

echo "🔄 Checking for migration conflicts..."
python manage.py migrate --fake contenttypes zero --settings=core.settings.prod || true
python manage.py migrate --fake auth zero --settings=core.settings.prod || true
python manage.py migrate --fake sessions zero --settings=core.settings.prod || true
python manage.py migrate --fake sites zero --settings=core.settings.prod || true
python manage.py migrate --fake account zero --settings=core.settings.prod || true
python manage.py migrate --fake socialaccount zero --settings=core.settings.prod || true
python manage.py migrate --fake authtoken zero --settings=core.settings.prod || true
python manage.py migrate --fake users zero --settings=core.settings.prod || true
python manage.py migrate --fake health zero --settings=core.settings.prod || true

# Make fresh migrations
echo "🔧 Creating fresh migrations..."
python manage.py makemigrations users --settings=core.settings.prod
python manage.py makemigrations health --settings=core.settings.prod

# Apply all migrations from scratch with fake-initial
echo "🚀 Applying all migrations with fake-initial..."
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