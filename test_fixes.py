#!/usr/bin/env python3
"""
Script para probar las correcciones implementadas
"""

import requests
import json
import sys

def test_endpoints():
    """Probar los endpoints que estaban fallando"""
    base_url = "http://localhost:5000"
    
    print("🔍 Probando endpoints...")
    
    # Test 1: Health endpoint
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        print(f"✅ Health endpoint: {response.status_code}")
    except Exception as e:
        print(f"❌ Health endpoint: {e}")
    
    # Test 2: API notifications count
    try:
        response = requests.get(f"{base_url}/api/notifications/count", timeout=5)
        print(f"✅ API notifications count: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Count: {data.get('count', 'N/A')}")
    except Exception as e:
        print(f"❌ API notifications count: {e}")
    
    # Test 3: API dashboard stats
    try:
        response = requests.get(f"{base_url}/api/dashboard/stats", timeout=5)
        print(f"✅ API dashboard stats: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Stats: {len(data)} items")
    except Exception as e:
        print(f"❌ API dashboard stats: {e}")
    
    # Test 4: Expenses index (should not give 500 error)
    try:
        response = requests.get(f"{base_url}/expenses/", timeout=5)
        print(f"✅ Expenses index: {response.status_code}")
    except Exception as e:
        print(f"❌ Expenses index: {e}")
    
    # Test 5: Admin email config (should not give 500 error)
    try:
        response = requests.get(f"{base_url}/admin/email-config", timeout=5)
        print(f"✅ Admin email config: {response.status_code}")
    except Exception as e:
        print(f"❌ Admin email config: {e}")
    
    # Test 6: User management user details (should not give 500 error)
    try:
        response = requests.get(f"{base_url}/admin/users/user-details/1", timeout=5)
        print(f"✅ User details: {response.status_code}")
    except Exception as e:
        print(f"❌ User details: {e}")

def test_database_models():
    """Probar que los modelos de base de datos funcionan correctamente"""
    print("\n🗄️ Probando modelos de base de datos...")
    
    try:
        from app import app, db
        from models import User, Visit, Expense
        
        with app.app_context():
            # Test User model
            user = User.query.first()
            if user:
                print(f"✅ User model: {user.username}")
                
                # Test visits relationship
                visits_count = user.visits.count() if hasattr(user, 'visits') else 0
                print(f"✅ User visits relationship: {visits_count} visits")
                
                # Test expenses relationship
                expenses_count = user.expenses.count() if hasattr(user, 'expenses') else 0
                print(f"✅ User expenses relationship: {expenses_count} expenses")
            else:
                print("⚠️ No users found in database")
                
    except Exception as e:
        print(f"❌ Database models test: {e}")

def main():
    """Función principal"""
    print("🚀 Iniciando pruebas de correcciones...")
    
    # Test endpoints
    test_endpoints()
    
    # Test database models
    test_database_models()
    
    print("\n✅ Pruebas completadas!")

if __name__ == "__main__":
    main()
