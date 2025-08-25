"""
Fallback app.py for Render.com compatibility
This file exists to handle cases where Render tries to run 'gunicorn app:app'
"""

import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

try:
    # Try to import the app from wsgi.py
    from wsgi import app
    print("✅ Successfully imported app from wsgi.py")
except ImportError as e:
    print(f"❌ Error importing from wsgi.py: {e}")
    # Fallback: create a minimal Flask app
    from flask import Flask
    app = Flask(__name__)
    
    @app.route('/')
    def home():
        return "Application is running (fallback mode)"
    
    @app.route('/health')
    def health():
        return "OK"
    
    print("⚠️ Using fallback Flask app")

# Ensure the app is available for gunicorn
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
