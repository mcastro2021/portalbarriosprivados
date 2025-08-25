"""
Primary app.py for Render.com compatibility
This is the main entry point that Render will use when running 'gunicorn app:app'
"""

import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

print("🚀 Starting Primary App Entry Point...")

try:
    # Import and use the smart WSGI application
    from smart_wsgi import app
    print("✅ Successfully imported smart WSGI application")
    print(f"✅ App type: {type(app)}")
except ImportError as e:
    print(f"❌ Error importing smart WSGI: {e}")
    
    # Fallback to standalone WSGI
    try:
        from standalone_wsgi import app
        print("✅ Successfully imported standalone WSGI application")
        print(f"✅ App type: {type(app)}")
    except ImportError as e2:
        print(f"❌ Error importing standalone WSGI: {e2}")
        
        # Ultimate fallback - create a minimal Flask app
        try:
            from flask import Flask, jsonify
            app = Flask(__name__)
            
            @app.route('/')
            def home():
                return jsonify({
                    'status': 'ultimate_fallback',
                    'message': 'Application is running in ultimate fallback mode',
                    'error': f'Smart WSGI failed: {e}, Standalone WSGI failed: {e2}'
                })
            
            @app.route('/health')
            def health():
                return jsonify({
                    'status': 'ultimate_fallback_health',
                    'message': 'Ultimate fallback health check'
                })
            
            @app.route('/auth/login', methods=['GET', 'POST'])
            def fallback_login():
                return jsonify({
                    'status': 'error',
                    'message': 'Login endpoint not available in ultimate fallback mode',
                    'error': 'All WSGI systems failed to load'
                }), 500
            
            print("⚠️ Using ultimate fallback Flask app")
            
        except ImportError as e3:
            print(f"❌ Flask also not available: {e3}")
            
            # Final fallback - pure WSGI
            class FinalFallback:
                def __call__(self, environ, start_response):
                    status = '200 OK'
                    headers = [('Content-Type', 'application/json')]
                    start_response(status, headers)
                    return [b'{"status": "final_fallback", "message": "All systems failed"}']
            
            app = FinalFallback()
            print("⚠️ Using final fallback WSGI app")

# Ensure the app is available for gunicorn
if __name__ == '__main__':
    if hasattr(app, 'run'):
        app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
    else:
        print("❌ Cannot run directly - use with Gunicorn")
