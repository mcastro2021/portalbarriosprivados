"""
WSGI entry point for the application.
This file is used by gunicorn and other WSGI servers.
"""

from app import app

if __name__ == "__main__":
    app.run()
