#!/usr/bin/env python3
"""
Script de configuración mejorada para Portal Barrios Privados
Integra todas las mejoras implementadas
"""

import os
import sys
import secrets
import subprocess
from pathlib import Path
from app.core.config_validator import ConfigValidator
from app.services.cache_service import CacheService
from app.services.query_optimizer import QueryOptimizer
from app.utils.asset_optimizer import AssetOptimizer


class ImprovedSetup:
    """Configuración mejorada del proyecto"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.services_initialized = False
        
    def run_setup(self):
        """Ejecutar configuración completa mejorada"""
        print("🏠 Portal Barrios Privados - Configuración Mejorada")
        print("=" * 60)
        
        steps = [
            ("Validar entorno", self.validate_environment),
            ("Instalar dependencias", self.install_dependencies),
            ("Configurar variables de entorno", self.setup_environment_variables),
            ("Inicializar base de datos", self.setup_database),
            ("Configurar servicios", self.setup_services),
            ("Optimizar base de datos", self.optimize_database),
            ("Construir assets", self.build_assets),
            ("Ejecutar tests", self.run_tests),
            ("Validar configuración final", self.final_validation)
        ]
        
        for step_name, step_func in steps:
            print(f"\n📋 {step_name}...")
            try:
                success = step_func()
                if success:
                    print(f"✅ {step_name} completado")
                else:
                    print(f"⚠️ {step_name} completado con advertencias")
            except Exception as e:
                print(f"❌ Error en {step_name}: {e}")
                response = input("¿Continuar con el siguiente paso? (y/N): ")
                if response.lower() != 'y':
                    print("Configuración cancelada.")
                    return False
        
        print("\n🎉 Configuración mejorada completada exitosamente!")
        self.show_next_steps()
        return True
    
    def validate_environment(self):
        """Validar entorno de desarrollo"""
        try:
            # Verificar Python version
            if sys.version_info < (3, 9):
                print("⚠️ Se recomienda Python 3.9 o superior")
            
            # Verificar pip
            subprocess.run([sys.executable, '-m', 'pip', '--version'], 
                         check=True, capture_output=True)
            
            # Verificar git
            subprocess.run(['git', '--version'], 
                         check=True, capture_output=True)
            
            # Verificar estructura de directorios
            required_dirs = ['app', 'static', 'templates', 'tests']
            for dir_name in required_dirs:
                dir_path = self.project_root / dir_name
                if not dir_path.exists():
                    print(f"⚠️ Directorio faltante: {dir_name}")
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"Error validando entorno: {e}")
            return False
    
    def install_dependencies(self):
        """Instalar dependencias mejoradas"""
        try:
            print("📦 Instalando dependencias...")
            
            # Actualizar pip
            subprocess.run([
                sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'
            ], check=True)
            
            # Instalar dependencias
            subprocess.run([
                sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'
            ], check=True)
            
            print("✅ Dependencias instaladas correctamente")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"Error instalando dependencias: {e}")
            return False
    
    def setup_environment_variables(self):
        """Configurar variables de entorno mejoradas"""
        try:
            env_file = self.project_root / '.env'
            
            if env_file.exists():
                response = input("El archivo .env ya existe. ¿Sobrescribir? (y/N): ")
                if response.lower() != 'y':
                    return True
            
            # Generar configuración mejorada
            secret_key = secrets.token_urlsafe(64)
            jwt_secret = secrets.token_urlsafe(32)
            
            env_content = f"""# Portal Barrios Privados - Configuración Mejorada
# Generado automáticamente con mejoras implementadas

# === CONFIGURACIÓN BÁSICA ===
SECRET_KEY={secret_key}
JWT_SECRET_KEY={jwt_secret}
FLASK_ENV=development
FLASK_DEBUG=True

# === BASE DE DATOS ===
SQLALCHEMY_DATABASE_URI=sqlite:///barrio_cerrado.db
# Para producción usar PostgreSQL:
# SQLALCHEMY_DATABASE_URI=postgresql://user:password@localhost/barrio_cerrado

# === REDIS CACHE ===
REDIS_URL=redis://localhost:6379/0
# Para desarrollo sin Redis, se usará cache en memoria

# === CONFIGURACIÓN DE EMAIL ===
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=
MAIL_PASSWORD=
MAIL_DEFAULT_SENDER=

# === MERCADOPAGO ===
MERCADOPAGO_ACCESS_TOKEN=
MERCADOPAGO_PUBLIC_KEY=

# === WHATSAPP/TWILIO ===
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_PHONE_NUMBER=

# === CHATBOT ===
CLAUDE_API_KEY=
OPENAI_API_KEY=

# === NOTIFICACIONES ===
NOTIFICATION_EMAIL_ENABLED=True
NOTIFICATION_WHATSAPP_ENABLED=False
NOTIFICATION_PUSH_ENABLED=True

# === SEGURIDAD ===
WTF_CSRF_ENABLED=True
SESSION_COOKIE_SECURE=False
SESSION_COOKIE_HTTPONLY=True
RATE_LIMITING_ENABLED=True

# === CONFIGURACIÓN DEL BARRIO ===
BARRIO_NAME=Mi Barrio Privado
BARRIO_ADDRESS=Dirección del Barrio
BARRIO_PHONE=+54 9 11 1234-5678
BARRIO_EMAIL=info@mibarrio.com

# === OPTIMIZACIONES ===
CACHE_ENABLED=True
QUERY_OPTIMIZATION_ENABLED=True
ASSET_OPTIMIZATION_ENABLED=True
WEBSOCKET_ENABLED=True

# === DESARROLLO ===
DEBUG_TOOLBAR_ENABLED=False
PROFILING_ENABLED=False
"""
            
            with open(env_file, 'w', encoding='utf-8') as f:
                f.write(env_content)
            
            print("✅ Archivo .env creado con configuración mejorada")
            return True
            
        except Exception as e:
            print(f"Error configurando variables de entorno: {e}")
            return False
    
    def setup_database(self):
        """Configurar base de datos con optimizaciones"""
        try:
            print("🗄️ Configurando base de datos...")
            
            # Importar app para contexto
            from app import create_app
            from models import db
            
            app = create_app('development')
            with app.app_context():
                # Crear tablas
                db.create_all()
                print("✅ Tablas de base de datos creadas")
                
                # Crear usuario administrador
                from models import User
                admin = User.query.filter_by(username='admin').first()
                if not admin:
                    admin = User(
                        username='admin',
                        email='admin@barrioprivado.com',
                        name='Administrador del Sistema',
                        role='admin',
                        is_active=True,
                        email_verified=True
                    )
                    admin.set_password('Admin123!')
                    db.session.add(admin)
                    db.session.commit()
                    print("✅ Usuario administrador creado (admin/Admin123!)")
                
                # Inicializar migraciones
                if not os.path.exists('migrations'):
                    subprocess.run(['flask', 'db', 'init'], check=True)
                    print("✅ Sistema de migraciones inicializado")
                
                # Crear migración inicial
                try:
                    subprocess.run(['flask', 'db', 'migrate', '-m', 'Initial migration with improvements'], 
                                 check=True, capture_output=True)
                    print("✅ Migración inicial creada")
                except subprocess.CalledProcessError:
                    print("ℹ️ Migración ya existe o no es necesaria")
            
            return True
            
        except Exception as e:
            print(f"Error configurando base de datos: {e}")
            return False
    
    def setup_services(self):
        """Configurar servicios mejorados"""
        try:
            print("⚙️ Configurando servicios...")
            
            from app import create_app
            from app.services.cache_service import CacheService
            from app.services.websocket_service import WebSocketService
            
            app = create_app('development')
            with app.app_context():
                # Inicializar cache service
                CacheService.init_app(app)
                print("✅ Cache service configurado")
                
                # Inicializar WebSocket service
                WebSocketService.init_app(app)
                print("✅ WebSocket service configurado")
                
                self.services_initialized = True
            
            return True
            
        except Exception as e:
            print(f"Error configurando servicios: {e}")
            return False
    
    def optimize_database(self):
        """Optimizar base de datos"""
        try:
            print("🚀 Optimizando base de datos...")
            
            from app import create_app
            
            app = create_app('development')
            with app.app_context():
                # Crear índices
                result = QueryOptimizer.create_indexes()
                if 'error' not in result:
                    print(f"✅ Índices creados: {result['indexes_created']}/{result['total_attempted']}")
                
                # Optimizar base de datos
                optimization_result = QueryOptimizer.optimize_database()
                if 'error' not in optimization_result:
                    print("✅ Base de datos optimizada")
                
                # Obtener estadísticas
                stats = QueryOptimizer.get_query_performance_stats()
                if 'error' not in stats:
                    print(f"📊 Estadísticas: {stats.get('users_count', 0)} usuarios, "
                          f"{stats.get('cache', {}).get('type', 'memory')} cache")
            
            return True
            
        except Exception as e:
            print(f"Error optimizando base de datos: {e}")
            return False
    
    def build_assets(self):
        """Construir y optimizar assets"""
        try:
            print("🎨 Construyendo assets...")
            
            optimizer = AssetOptimizer()
            
            # Crear directorios necesarios
            static_dirs = ['static/dist', 'static/css', 'static/js', 'static/images']
            for dir_path in static_dirs:
                os.makedirs(dir_path, exist_ok=True)
            
            # Crear archivos CSS y JS básicos si no existen
            css_file = Path('static/css/style.css')
            if not css_file.exists():
                css_content = """/* Portal Barrios Privados - Estilos mejorados */
.dashboard-card {
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    cursor: pointer;
}

.dashboard-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.card-hover {
    background-color: #f8f9fa;
}

.notification-toast {
    min-width: 300px;
    margin-bottom: 10px;
}

.activity-item {
    display: flex;
    align-items: center;
    padding: 10px;
    border-bottom: 1px solid #eee;
    transition: background-color 0.2s ease;
}

.activity-item:hover {
    background-color: #f8f9fa;
}

.new-activity {
    animation: slideIn 0.5s ease;
    background-color: #e3f2fd;
}

@keyframes slideIn {
    from { transform: translateX(-100%); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
}

.spinning {
    animation: spin 1s linear infinite;
}

@keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}

.status-connected {
    color: #28a745;
}

.status-disconnected {
    color: #dc3545;
}
"""
                css_file.write_text(css_content, encoding='utf-8')
                print("✅ Archivo CSS básico creado")
            
            js_file = Path('static/js/app.js')
            if not js_file.exists():
                js_content = """// Portal Barrios Privados - JavaScript mejorado
console.log('Portal Barrios Privados - Versión mejorada cargada');

// Utilidades globales
window.PortalUtils = {
    formatDate: function(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('es-ES');
    },
    
    showToast: function(message, type = 'info') {
        // Implementación básica de toast
        const toast = document.createElement('div');
        toast.className = `alert alert-${type} toast-message`;
        toast.textContent = message;
        toast.style.cssText = 'position: fixed; top: 20px; right: 20px; z-index: 9999;';
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
            if (toast.parentElement) {
                toast.remove();
            }
        }, 3000);
    }
};
"""
                js_file.write_text(js_content, encoding='utf-8')
                print("✅ Archivo JS básico creado")
            
            # Construir assets
            results = optimizer.build_all_assets()
            
            if 'error' not in results:
                css_count = len([r for r in results.get('css', []) if r.get('success')])
                js_count = len([r for r in results.get('js', []) if r.get('success')])
                print(f"✅ Assets construidos: {css_count} CSS, {js_count} JS")
                
                # Mostrar estadísticas de imágenes si se optimizaron
                img_stats = results.get('images', {})
                if img_stats.get('processed', 0) > 0:
                    savings = img_stats.get('savings_percent', 0)
                    print(f"✅ Imágenes optimizadas: {img_stats['processed']} archivos, "
                          f"{savings:.1f}% de ahorro")
            
            return True
            
        except Exception as e:
            print(f"Error construyendo assets: {e}")
            return False
    
    def run_tests(self):
        """Ejecutar tests básicos"""
        try:
            print("🧪 Ejecutando tests...")
            
            # Verificar si pytest está disponible
            try:
                import pytest
            except ImportError:
                print("⚠️ pytest no disponible, saltando tests")
                return True
            
            # Ejecutar tests básicos
            test_result = subprocess.run([
                sys.executable, '-m', 'pytest', 'tests/', '-v', '--tb=short'
            ], capture_output=True, text=True)
            
            if test_result.returncode == 0:
                print("✅ Tests ejecutados correctamente")
            else:
                print("⚠️ Algunos tests fallaron, pero continuando...")
                print(test_result.stdout[-500:])  # Mostrar últimas líneas
            
            return True
            
        except Exception as e:
            print(f"Error ejecutando tests: {e}")
            return False
    
    def final_validation(self):
        """Validación final de configuración"""
        try:
            print("🔍 Validación final...")
            
            # Validar configuración
            result = ConfigValidator.validate_environment_variables()
            
            if result.is_valid:
                print("✅ Configuración válida")
            else:
                print("⚠️ Configuración con errores:")
                for error in result.errors[:3]:  # Mostrar solo primeros 3
                    print(f"  - {error}")
            
            if result.warnings:
                print("💡 Advertencias:")
                for warning in result.warnings[:3]:
                    print(f"  - {warning}")
            
            return True
            
        except Exception as e:
            print(f"Error en validación final: {e}")
            return False
    
    def show_next_steps(self):
        """Mostrar próximos pasos"""
        print("\n" + "=" * 60)
        print("🎯 PRÓXIMOS PASOS")
        print("=" * 60)
        
        print("\n1. 🚀 Iniciar la aplicación:")
        print("   python app.py")
        
        print("\n2. 🌐 Acceder al sistema:")
        print("   http://localhost:5000")
        print("   Usuario: admin")
        print("   Contraseña: Admin123!")
        
        print("\n3. ⚙️ Configurar servicios opcionales:")
        print("   - Editar .env para email, WhatsApp, MercadoPago")
        print("   - Configurar Redis para mejor rendimiento")
        print("   - Configurar PostgreSQL para producción")
        
        print("\n4. 🧪 Ejecutar tests:")
        print("   pytest tests/ -v")
        
        print("\n5. 📊 Monitorear rendimiento:")
        print("   - /api/v1/health - Estado de la API")
        print("   - Dashboard de administrador para estadísticas")
        
        print("\n6. 🔧 Optimizaciones adicionales:")
        print("   - python -c \"from app.services.query_optimizer import QueryOptimizer; QueryOptimizer.optimize_database()\"")
        print("   - python -c \"from app.utils.asset_optimizer import AssetOptimizer; AssetOptimizer().build_all_assets()\"")
        
        print("\n📚 Documentación:")
        print("   - README_MEJORAS_CRITICAS.md")
        print("   - Código fuente en app/services/ y app/api/")


def main():
    """Función principal"""
    setup = ImprovedSetup()
    
    print("¿Desea ejecutar la configuración mejorada completa? (Y/n): ", end="")
    response = input().strip().lower()
    
    if response in ('', 'y', 'yes', 'sí', 'si'):
        success = setup.run_setup()
        sys.exit(0 if success else 1)
    else:
        print("Configuración cancelada.")
        sys.exit(0)


if __name__ == '__main__':
    main()
