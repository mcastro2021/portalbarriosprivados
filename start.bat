@echo off
echo Starting application with gunicorn wsgi:app
gunicorn wsgi:app --bind 0.0.0.0:%PORT% --workers 1 --timeout 120 --threads 2
