#!/usr/bin/env python3
"""
Test script to verify deployment environment
"""

import sys
import os

def test_imports():
    """Test if all required modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        import flask
        print("✅ Flask imported successfully")
        print(f"   Flask version: {flask.__version__}")
    except ImportError as e:
        print(f"❌ Flask import failed: {e}")
        return False
    
    try:
        from flask import Flask
        print("✅ Flask.Flask imported successfully")
    except ImportError as e:
        print(f"❌ Flask.Flask import failed: {e}")
        return False
    
    try:
        import gunicorn
        print("✅ Gunicorn imported successfully")
    except ImportError as e:
        print(f"❌ Gunicorn import failed: {e}")
    
    return True

def test_app_creation():
    """Test if we can create a Flask app"""
    print("\n🔍 Testing app creation...")
    
    try:
        from flask import Flask
        app = Flask(__name__)
        print("✅ Flask app created successfully")
        return True
    except Exception as e:
        print(f"❌ Flask app creation failed: {e}")
        return False

def test_main_import():
    """Test if main.py can be imported"""
    print("\n🔍 Testing main.py import...")
    
    try:
        import main
        print("✅ main.py imported successfully")
        return True
    except Exception as e:
        print(f"❌ main.py import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_wsgi_import():
    """Test if wsgi.py can be imported"""
    print("\n🔍 Testing wsgi.py import...")
    
    try:
        import wsgi
        print("✅ wsgi.py imported successfully")
        return True
    except Exception as e:
        print(f"❌ wsgi.py import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("🚀 Starting deployment environment tests...")
    print(f"Python version: {sys.version}")
    print(f"Current directory: {os.getcwd()}")
    print(f"Files in directory: {os.listdir('.')}")
    
    success = True
    
    if not test_imports():
        success = False
    
    if not test_app_creation():
        success = False
    
    if not test_main_import():
        success = False
    
    if not test_wsgi_import():
        success = False
    
    print(f"\n{'✅' if success else '❌'} All tests {'passed' if success else 'failed'}")
    return success

if __name__ == "__main__":
    main()
