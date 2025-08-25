# Web process - Standalone WSGI application (no Flask dependencies)
web: gunicorn standalone_wsgi:app --bind 0.0.0.0:$PORT --workers 1 --timeout 120 --threads 2
