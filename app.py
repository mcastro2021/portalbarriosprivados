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
    from flask import Flask, jsonify
    app = Flask(__name__)
    
    @app.route('/')
    def home():
        return jsonify({
            'status': 'fallback_mode',
            'message': 'Application is running in fallback mode',
            'error': str(e) if 'e' in locals() else 'Unknown import error'
        })
    
    @app.route('/health')
    def health():
        return jsonify({
            'status': 'fallback_health',
            'message': 'Fallback health check'
        })
    
    @app.route('/diagnostic')
    def diagnostic():
        return jsonify({
            'status': 'fallback_diagnostic',
            'message': 'Running in fallback mode due to import errors',
            'python_path': sys.path,
            'current_dir': os.getcwd(),
            'files_in_dir': os.listdir('.'),
            'error': str(e) if 'e' in locals() else 'Unknown error'
        })
    
    @app.route('/auth/login', methods=['GET', 'POST'])
    def fallback_login():
        return jsonify({
            'status': 'error',
            'message': 'Login endpoint not available in fallback mode',
            'error': 'Application is running in fallback mode due to import errors'
        }), 500
    
    print("⚠️ Using fallback Flask app")

# Ensure the app is available for gunicorn
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
