#!/usr/bin/env bash
# Exit on error

set -o errexit
pip install --upgrade pip
pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
DJANGO_SUPERUSER_USERNAME=admin1 \
DJANGO_SUPERUSER_EMAIL=admin@email.com \
DJANGO_SUPERUSER_PASSWORD=1234 \
python manage.py createsuperuser --noinput || true