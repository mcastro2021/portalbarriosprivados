#!/usr/bin/env python3
"""
Standalone WSGI application that works without Flask
This is a fallback solution for when Flask is not available
"""

import os
import sys
import json
import traceback
from urllib.parse import parse_qs, urlparse

class StandaloneWSGI:
    """Standalone WSGI application that provides basic functionality"""
    
    def __init__(self):
        self.routes = {
            '/': self.home,
            '/health': self.health,
            '/diagnostic': self.diagnostic,
            '/auth/login': self.login,
            '/api/notifications': self.notifications,
        }
    
    def __call__(self, environ, start_response):
        """WSGI entry point"""
        try:
            path = environ.get('PATH_INFO', '/')
            method = environ.get('REQUEST_METHOD', 'GET')
            
            # Handle CORS preflight
            if method == 'OPTIONS':
                return self.handle_cors(start_response)
            
            # Route the request
            if path in self.routes:
                return self.routes[path](environ, start_response)
            else:
                return self.not_found(environ, start_response)
                
        except Exception as e:
            return self.internal_error(environ, start_response, str(e))
    
    def handle_cors(self, start_response):
        """Handle CORS preflight requests"""
        headers = [
            ('Content-Type', 'application/json'),
            ('Access-Control-Allow-Origin', '*'),
            ('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS'),
            ('Access-Control-Allow-Headers', 'Content-Type, Authorization'),
        ]
        start_response('200 OK', headers)
        return [b'']
    
    def home(self, environ, start_response):
        """Home page"""
        response_data = {
            'status': 'standalone_mode',
            'message': 'Application is running in standalone mode',
            'reason': 'Flask dependencies not available',
            'endpoints': list(self.routes.keys())
        }
        
        headers = [
            ('Content-Type', 'application/json'),
            ('Access-Control-Allow-Origin', '*'),
        ]
        start_response('200 OK', headers)
        return [json.dumps(response_data).encode('utf-8')]
    
    def health(self, environ, start_response):
        """Health check endpoint"""
        response_data = {
            'status': 'standalone_health',
            'message': 'Application is running in standalone mode',
            'healthy': True
        }
        
        headers = [
            ('Content-Type', 'application/json'),
            ('Access-Control-Allow-Origin', '*'),
        ]
        start_response('200 OK', headers)
        return [json.dumps(response_data).encode('utf-8')]
    
    def diagnostic(self, environ, start_response):
        """Diagnostic endpoint"""
        response_data = {
            'status': 'standalone_diagnostic',
            'message': 'Running in standalone WSGI mode',
            'python_version': sys.version,
            'current_directory': os.getcwd(),
            'files_in_directory': os.listdir('.'),
            'environment_vars': dict(os.environ),
            'wsgi_mode': True
        }
        
        headers = [
            ('Content-Type', 'application/json'),
            ('Access-Control-Allow-Origin', '*'),
        ]
        start_response('200 OK', headers)
        return [json.dumps(response_data, default=str).encode('utf-8')]
    
    def login(self, environ, start_response):
        """Login endpoint - returns error in standalone mode"""
        response_data = {
            'status': 'error',
            'message': 'Login endpoint not available in standalone mode',
            'error': 'Flask dependencies not installed',
            'standalone_mode': True
        }
        
        headers = [
            ('Content-Type', 'application/json'),
            ('Access-Control-Allow-Origin', '*'),
        ]
        start_response('500 Internal Server Error', headers)
        return [json.dumps(response_data).encode('utf-8')]
    
    def notifications(self, environ, start_response):
        """Notifications endpoint - returns empty array"""
        response_data = {
            'notifications': [],
            'count': 0,
            'standalone_mode': True
        }
        
        headers = [
            ('Content-Type', 'application/json'),
            ('Access-Control-Allow-Origin', '*'),
        ]
        start_response('200 OK', headers)
        return [json.dumps(response_data).encode('utf-8')]
    
    def not_found(self, environ, start_response):
        """404 handler"""
        response_data = {
            'status': 'error',
            'message': 'Endpoint not found',
            'path': environ.get('PATH_INFO', '/'),
            'standalone_mode': True
        }
        
        headers = [
            ('Content-Type', 'application/json'),
            ('Access-Control-Allow-Origin', '*'),
        ]
        start_response('404 Not Found', headers)
        return [json.dumps(response_data).encode('utf-8')]
    
    def internal_error(self, environ, start_response, error_message):
        """500 handler"""
        response_data = {
            'status': 'error',
            'message': 'Internal server error',
            'error': error_message,
            'standalone_mode': True
        }
        
        headers = [
            ('Content-Type', 'application/json'),
            ('Access-Control-Allow-Origin', '*'),
        ]
        start_response('500 Internal Server Error', headers)
        return [json.dumps(response_data).encode('utf-8')]

# Create the application instance
print("🚀 Starting Standalone WSGI Application...")
print("⚠️ Running in standalone mode - Flask not available")

# Create the WSGI application
app = StandaloneWSGI()

# For compatibility with gunicorn
application = app

if __name__ == "__main__":
    print("❌ This application should be run with Gunicorn")
    print("   Command: gunicorn standalone_wsgi:app")
