#!/bin/sh
set -eu #exit when e - error a and u- when undefine var

python manage.py migrate --noinput #migrate all without asking
python manage.py collectstatic --noinput #collect all the static

# Replace the shell with Gunicorn so it receives container signals directly.
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers "${WEB_CONCURRENCY:-1}" \
    --access-logfile -