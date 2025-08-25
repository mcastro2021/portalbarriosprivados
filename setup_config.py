#!/usr/bin/env python3
"""
Script de configuración y validación para Portal Barrios Privados
"""

import os
import sys
import secrets
from app.core.config_validator import ConfigValidator


def generate_secret_key():
    """Generar clave secreta segura"""
    return secrets.token_urlsafe(64)


def create_env_file():
    """Crear archivo .env con configuración básica"""
    if os.path.exists('.env'):
        response = input("El archivo .env ya existe. ¿Desea sobrescribirlo? (y/N): ")
        if response.lower() != 'y':
            print("Operación cancelada.")
            return
    
    # Generar configuración básica
    secret_key = generate_secret_key()
    
    env_content = f"""# Configuración de Portal Barrios Privados
# Generado automáticamente - Complete los valores faltantes

# === CONFIGURACIÓN REQUERIDA ===
SECRET_KEY={secret_key}
SQLALCHEMY_DATABASE_URI=sqlite:///barrio_cerrado.db

# === CONFIGURACIÓN DE DESARROLLO ===
FLASK_ENV=development
FLASK_DEBUG=True

# === CONFIGURACIÓN DE EMAIL (Opcional) ===
#MAIL_SERVER=smtp.gmail.com
#MAIL_PORT=587
#MAIL_USE_TLS=True
#MAIL_USERNAME=tu_email@gmail.com
#MAIL_PASSWORD=tu_password_de_aplicacion
#MAIL_DEFAULT_SENDER=tu_email@gmail.com

# === CONFIGURACIÓN DE MERCADOPAGO (Opcional) ===
#MERCADOPAGO_ACCESS_TOKEN=TU_ACCESS_TOKEN_MERCADOPAGO
#MERCADOPAGO_PUBLIC_KEY=TU_PUBLIC_KEY_MERCADOPAGO

# === CONFIGURACIÓN DE WHATSAPP/TWILIO (Opcional) ===
#TWILIO_ACCOUNT_SID=tu_account_sid
#TWILIO_AUTH_TOKEN=tu_auth_token
#TWILIO_PHONE_NUMBER=+1234567890

# === CONFIGURACIÓN DE CHATBOT (Opcional) ===
#CLAUDE_API_KEY=tu_claude_api_key
#OPENAI_API_KEY=tu_openai_api_key

# === CONFIGURACIÓN DE NOTIFICACIONES ===
NOTIFICATION_EMAIL_ENABLED=True
NOTIFICATION_WHATSAPP_ENABLED=False
NOTIFICATION_PUSH_ENABLED=True

# === CONFIGURACIÓN DE SEGURIDAD ===
WTF_CSRF_ENABLED=True
SESSION_COOKIE_SECURE=False
SESSION_COOKIE_HTTPONLY=True

# === CONFIGURACIÓN DEL BARRIO ===
BARRIO_NAME=Mi Barrio Privado
BARRIO_ADDRESS=Dirección del Barrio
BARRIO_PHONE=+54 9 11 1234-5678
BARRIO_EMAIL=info@mibarrio.com
"""
    
    with open('.env', 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print("✅ Archivo .env creado exitosamente")
    print("📝 Complete las configuraciones opcionales según sus necesidades")


def validate_current_config():
    """Validar configuración actual"""
    print("🔍 Validando configuración actual...")
    
    # Cargar variables de entorno
    from dotenv import load_dotenv
    load_dotenv()
    
    # Validar configuración
    result = ConfigValidator.validate_environment_variables()
    
    # Mostrar reporte
    ConfigValidator.print_validation_report(result)
    
    return result.is_valid


def setup_database():
    """Configurar base de datos"""
    print("🗄️  Configurando base de datos...")
    
    try:
        # Importar app para inicializar contexto
        from app import create_app
        from models import db
        
        app = create_app()
        with app.app_context():
            # Crear tablas
            db.create_all()
            print("✅ Base de datos inicializada")
            
            # Crear migración inicial si no existe
            if not os.path.exists('migrations'):
                os.system('flask db init')
                print("✅ Sistema de migraciones inicializado")
            
            # Crear primera migración
            os.system('flask db migrate -m "Initial migration"')
            print("✅ Migración inicial creada")
            
    except Exception as e:
        print(f"❌ Error configurando base de datos: {e}")
        return False
    
    return True


def install_dependencies():
    """Instalar dependencias"""
    print("📦 Instalando dependencias...")
    
    try:
        os.system('pip install -r requirements.txt')
        print("✅ Dependencias instaladas")
        return True
    except Exception as e:
        print(f"❌ Error instalando dependencias: {e}")
        return False


def main():
    """Función principal"""
    print("🏠 Portal Barrios Privados - Configuración Inicial")
    print("=" * 50)
    
    # Menú de opciones
    while True:
        print("\nOpciones disponibles:")
        print("1. Crear archivo .env")
        print("2. Validar configuración actual")
        print("3. Instalar dependencias")
        print("4. Configurar base de datos")
        print("5. Configuración completa (todo)")
        print("6. Generar template de .env")
        print("0. Salir")
        
        choice = input("\nSeleccione una opción: ").strip()
        
        if choice == '1':
            create_env_file()
        
        elif choice == '2':
            validate_current_config()
        
        elif choice == '3':
            install_dependencies()
        
        elif choice == '4':
            setup_database()
        
        elif choice == '5':
            print("🚀 Ejecutando configuración completa...")
            
            # Paso 1: Crear .env
            create_env_file()
            
            # Paso 2: Instalar dependencias
            if not install_dependencies():
                print("❌ Error en la instalación. Abortando.")
                continue
            
            # Paso 3: Validar configuración
            if not validate_current_config():
                print("⚠️  Configuración con errores, pero continuando...")
            
            # Paso 4: Configurar base de datos
            if setup_database():
                print("🎉 Configuración completa exitosa!")
                print("\n📋 Próximos pasos:")
                print("1. Complete las configuraciones opcionales en .env")
                print("2. Ejecute: python app.py")
                print("3. Visite: http://localhost:5000")
            else:
                print("❌ Error en la configuración de base de datos")
        
        elif choice == '6':
            template = ConfigValidator.get_config_template()
            with open('.env.template', 'w', encoding='utf-8') as f:
                f.write(template)
            print("✅ Template .env.template creado")
        
        elif choice == '0':
            print("👋 ¡Hasta luego!")
            break
        
        else:
            print("❌ Opción inválida")


if __name__ == '__main__':
    main()
