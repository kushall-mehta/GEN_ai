#!/bin/sh
set -eu #exit when e - error a and u- when undefine var

python manage.py migrate --noinput #migrate all without asking
python manage.py collectstatic --noinput #collect all the static

# Replace the shell with Gunicorn so it receives container signals directly.
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --timeout 90 \
    --workers "${WEB_CONCURRENCY:-1}" \
    --access-logfile -

#port
#This controls the number of Gunicorn worker
#Send access logs to standard output.
#entrypoint.sh → tells the container what to do when it starts

#entrypoint.sh used to automate the commands that need to run when the application starts, such as database migrations, static-file collection, and starting the application server