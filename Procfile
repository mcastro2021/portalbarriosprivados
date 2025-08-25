# Web process - Smart WSGI application (tries Flask first, then standalone)
web: gunicorn smart_wsgi:app --bind 0.0.0.0:$PORT --workers 1 --timeout 120 --threads 2
