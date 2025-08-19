#!/usr/bin/env python3
"""
Script de configuración para el chatbot con Claude API
"""

import os
import sys
import subprocess

def print_banner():
    """Imprimir banner del script"""
    print("=" * 60)
    print("🤖 CONFIGURACIÓN DEL CHATBOT CON CLAUDE API")
    print("=" * 60)
    print()

def check_python_version():
    """Verificar versión de Python"""
    if sys.version_info < (3, 8):
        print("❌ Error: Se requiere Python 3.8 o superior")
        print(f"   Versión actual: {sys.version}")
        return False
    print(f"✅ Python {sys.version.split()[0]} - OK")
    return True

def install_dependencies():
    """Instalar dependencias necesarias"""
    print("📦 Instalando dependencias...")
    
    try:
        # Instalar anthropic
        subprocess.check_call([sys.executable, "-m", "pip", "install", "anthropic==0.18.1"])
        print("✅ anthropic instalado correctamente")
        
        # Verificar si openai está instalado
        try:
            import openai
            print("✅ openai ya está instalado")
        except ImportError:
            print("📦 Instalando openai...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "openai==1.35.0"])
            print("✅ openai instalado correctamente")
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Error instalando dependencias: {e}")
        return False
    
    return True

def create_env_file():
    """Crear archivo .env con configuración de Claude"""
    env_file = ".env"
    
    if os.path.exists(env_file):
        print(f"📄 Archivo {env_file} ya existe")
        response = input("¿Quieres sobrescribirlo? (y/N): ").lower()
        if response != 'y':
            print("⏭️ Saltando creación del archivo .env")
            return True
    
    print("📝 Creando archivo .env...")
    
    env_content = """# Configuración de la aplicación
SECRET_KEY=your-secret-key-here-change-in-production
FLASK_ENV=development
DATABASE_URL=sqlite:///barrio_cerrado.db

# Claude API (prioridad alta para el chatbot)
CLAUDE_API_KEY=your-claude-api-key-here
CLAUDE_MODEL=claude-3-sonnet-20240229

# OpenAI API (respaldo para el chatbot)
OPENAI_API_KEY=your-openai-api-key-here

# Configuración de email (opcional)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com

# MercadoPago (opcional para pagos)
MERCADOPAGO_ACCESS_TOKEN=your-mercadopago-access-token
MERCADOPAGO_PUBLIC_KEY=your-mercadopago-public-key

# WhatsApp/Twilio (opcional para notificaciones)
TWILIO_ACCOUNT_SID=your-twilio-account-sid
TWILIO_AUTH_TOKEN=your-twilio-auth-token
TWILIO_PHONE_NUMBER=your-twilio-whatsapp-number

# Redis (opcional para cache y tareas en segundo plano)
REDIS_URL=redis://localhost:6379/0

# Configuración de seguridad
SESSION_COOKIE_SECURE=False
WTF_CSRF_ENABLED=True

# Configuración de notificaciones
NOTIFICATION_EMAIL_ENABLED=True
NOTIFICATION_WHATSAPP_ENABLED=False
NOTIFICATION_PUSH_ENABLED=True

# Configuración del barrio
BARRIO_NAME=Barrio Tejas 4
BARRIO_ADDRESS=Dirección del Barrio
BARRIO_PHONE=+54 11 4444-5555
BARRIO_EMAIL=administracion@tejas4.com
"""
    
    try:
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(env_content)
        print(f"✅ Archivo {env_file} creado correctamente")
        return True
    except Exception as e:
        print(f"❌ Error creando archivo {env_file}: {e}")
        return False

def test_claude_connection():
    """Probar conexión con Claude API"""
    print("🧪 Probando conexión con Claude API...")
    
    # Verificar si hay API key configurada
    api_key = os.environ.get('CLAUDE_API_KEY')
    if not api_key or api_key == 'your-claude-api-key-here':
        print("⚠️  No se encontró CLAUDE_API_KEY válida")
        print("   Configura tu API key en el archivo .env")
        return False
    
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        
        # Test simple
        response = client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=50,
            messages=[{"role": "user", "content": "Di 'Hola' en español"}]
        )
        
        if response.content and len(response.content) > 0:
            print("✅ Conexión con Claude API exitosa")
            print(f"   Respuesta de prueba: {response.content[0].text.strip()}")
            return True
        else:
            print("❌ No se recibió respuesta de Claude API")
            return False
            
    except Exception as e:
        print(f"❌ Error conectando con Claude API: {e}")
        return False

def show_next_steps():
    """Mostrar próximos pasos"""
    print("\n" + "=" * 60)
    print("🎉 CONFIGURACIÓN COMPLETADA")
    print("=" * 60)
    print()
    print("📋 PRÓXIMOS PASOS:")
    print()
    print("1. 🔑 Obtén tu API key de Claude:")
    print("   • Ve a https://console.anthropic.com")
    print("   • Crea una cuenta o inicia sesión")
    print("   • Ve a 'API Keys' y crea una nueva key")
    print("   • Copia la key (comienza con 'sk-ant-...')")
    print()
    print("2. ⚙️ Configura tu API key:")
    print("   • Edita el archivo .env")
    print("   • Reemplaza 'your-claude-api-key-here' con tu API key real")
    print()
    print("3. 🚀 Ejecuta la aplicación:")
    print("   • python app.py")
    print("   • O: flask run")
    print()
    print("4. 🧪 Prueba el chatbot:")
    print("   • Ve a http://localhost:5000/chatbot")
    print("   • Escribe cualquier consulta")
    print("   • Claude debería responder de forma inteligente")
    print()
    print("📚 DOCUMENTACIÓN:")
    print("   • CHATBOT_CLAUDE_SETUP.md - Configuración detallada")
    print("   • CHATBOT_README.md - Funcionalidades del chatbot")
    print()
    print("🔧 SOLUCIÓN DE PROBLEMAS:")
    print("   • Si Claude no responde, verifica tu API key")
    print("   • El sistema usará OpenAI como respaldo automáticamente")
    print("   • Revisa los logs en la consola para errores")
    print()

def main():
    """Función principal"""
    print_banner()
    
    # Verificar Python
    if not check_python_version():
        sys.exit(1)
    
    print()
    
    # Instalar dependencias
    if not install_dependencies():
        print("❌ Error en la instalación de dependencias")
        sys.exit(1)
    
    print()
    
    # Crear archivo .env
    if not create_env_file():
        print("❌ Error creando archivo de configuración")
        sys.exit(1)
    
    print()
    
    # Cargar variables de entorno si existe .env
    if os.path.exists('.env'):
        try:
            from dotenv import load_dotenv
            load_dotenv()
            print("✅ Variables de entorno cargadas")
        except ImportError:
            print("⚠️  python-dotenv no está instalado, cargando .env manualmente")
            # Cargar .env manualmente
            with open('.env', 'r') as f:
                for line in f:
                    if line.strip() and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        os.environ[key] = value
    
    print()
    
    # Probar conexión (opcional)
    test_choice = input("¿Quieres probar la conexión con Claude API? (y/N): ").lower()
    if test_choice == 'y':
        test_claude_connection()
    
    print()
    show_next_steps()

if __name__ == "__main__":
    main()
