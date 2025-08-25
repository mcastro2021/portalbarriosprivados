#!/usr/bin/env python3
"""
Smart WSGI entry point that tries Flask first, then falls back to standalone
"""

import os
import sys

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

def create_smart_application():
    """Create the best available application"""
    print("🚀 Starting Smart WSGI Application...")
    
    # Try to import and use the full Flask application
    try:
        print("🔄 Attempting to load full Flask application...")
        from wsgi import app as flask_app
        print("✅ Full Flask application loaded successfully")
        return flask_app
    except Exception as e:
        print(f"⚠️ Full Flask application failed: {e}")
    
    # Try to import and use the main.py application
    try:
        print("🔄 Attempting to load main.py application...")
        from main import app as main_app
        print("✅ Main.py application loaded successfully")
        return main_app
    except Exception as e:
        print(f"⚠️ Main.py application failed: {e}")
    
    # Fall back to standalone WSGI application
    try:
        print("🔄 Falling back to standalone WSGI application...")
        from standalone_wsgi import app as standalone_app
        print("✅ Standalone WSGI application loaded successfully")
        return standalone_app
    except Exception as e:
        print(f"❌ Standalone WSGI application failed: {e}")
        raise Exception("No application could be loaded")
    
    # Ultimate fallback - create a minimal WSGI app
    print("🔄 Creating ultimate fallback WSGI application...")
    
    class UltimateFallback:
        def __call__(self, environ, start_response):
            status = '200 OK'
            headers = [('Content-Type', 'application/json')]
            start_response(status, headers)
            return [b'{"status": "fallback", "message": "Ultimate fallback mode"}']
    
    return UltimateFallback()

# Create the application
try:
    app = create_smart_application()
    application = app
    print(f"✅ Smart WSGI application created: {type(app)}")
except Exception as e:
    print(f"❌ Failed to create smart WSGI application: {e}")
    
    # Create a minimal fallback
    class MinimalFallback:
        def __call__(self, environ, start_response):
            status = '500 Internal Server Error'
            headers = [('Content-Type', 'application/json')]
            start_response(status, headers)
            return [b'{"error": "Application failed to start"}']
    
    app = MinimalFallback()
    application = app
    print("⚠️ Using minimal fallback application")

if __name__ == "__main__":
    print("❌ This application should be run with Gunicorn")
    print("   Command: gunicorn smart_wsgi:app")
