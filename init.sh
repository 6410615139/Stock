#!/bin/bash

# Apply migrations
echo "Applying migrations..."
python manage.py makemigrations
python manage.py migrate

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

python manage.py init_branch_list

# Create a superuser if not exists
echo "Creating superuser..."
python manage.py shell <<EOF
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin')
EOF

# Start the server
echo "Starting Django server..."
exec python manage.py runserver 0.0.0.0:8000
