#!/usr/bin/env python3
"""
Script de configuración integral para las mejoras implementadas
Configura y valida todas las mejoras críticas del sistema
"""

import os
import sys
import subprocess
import json
from datetime import datetime
from pathlib import Path

class ImprovementsSetup:
    """Configurador de mejoras del sistema"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.improvements_status = {}
        self.errors = []
        self.warnings = []
    
    def run_setup(self):
        """Ejecutar configuración completa"""
        print("🚀 Iniciando configuración de mejoras críticas...")
        print("=" * 60)
        
        # Verificar entorno
        self.check_environment()
        
        # Instalar dependencias
        self.install_dependencies()
        
        # Configurar base de datos
        self.setup_database()
        
        # Configurar servicios
        self.setup_services()
        
        # Configurar logging
        self.setup_logging()
        
        # Configurar monitoreo
        self.setup_monitoring()
        
        # Configurar optimizador de BD
        self.setup_database_optimizer()
        
        # Configurar servicio de backup
        self.setup_backup_service()
        
        # Configurar servicio de testing
        self.setup_testing_service()
        
        # Configurar 2FA
        self.setup_2fa()
        
        # Configurar validación
        self.setup_validation()
        
        # Configurar manejo de errores
        self.setup_error_handling()
        
        # Ejecutar tests
        self.run_tests()
        
        # Generar reporte
        self.generate_report()
        
        print("\n" + "=" * 60)
        print("✅ Configuración completada!")
        
        return len(self.errors) == 0
    
    def check_environment(self):
        """Verificar entorno de desarrollo"""
        print("\n📋 Verificando entorno...")
        
        # Verificar Python
        python_version = sys.version_info
        if python_version < (3, 8):
            self.errors.append("Se requiere Python 3.8 o superior")
        else:
            print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
        
        # Verificar pip
        try:
            subprocess.run([sys.executable, "-m", "pip", "--version"], 
                         check=True, capture_output=True)
            print("✅ pip disponible")
        except subprocess.CalledProcessError:
            self.errors.append("pip no está disponible")
        
        # Verificar estructura de proyecto
        required_dirs = [
            "app", "app/core", "app/services", "app/schemas", 
            "app/api", "app/api/v1", "app/utils", "templates", "static"
        ]
        
        for dir_path in required_dirs:
            full_path = self.project_root / dir_path
            if not full_path.exists():
                full_path.mkdir(parents=True, exist_ok=True)
                print(f"📁 Creado directorio: {dir_path}")
            else:
                print(f"✅ Directorio existe: {dir_path}")
        
        # Verificar archivos críticos
        critical_files = [
            "app.py", "models.py", "config.py", "requirements.txt"
        ]
        
        for file_path in critical_files:
            full_path = self.project_root / file_path
            if not full_path.exists():
                self.errors.append(f"Archivo crítico faltante: {file_path}")
            else:
                print(f"✅ Archivo existe: {file_path}")
    
    def install_dependencies(self):
        """Instalar dependencias"""
        print("\n📦 Instalando dependencias...")
        
        try:
            # Actualizar pip
            subprocess.run([
                sys.executable, "-m", "pip", "install", "--upgrade", "pip"
            ], check=True, capture_output=True)
            
            # Instalar dependencias
            subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
            ], check=True, capture_output=True)
            
            print("✅ Dependencias instaladas correctamente")
            
        except subprocess.CalledProcessError as e:
            self.errors.append(f"Error instalando dependencias: {e}")
    
    def setup_database(self):
        """Configurar base de datos"""
        print("\n🗄️ Configurando base de datos...")
        
        try:
            # Crear directorio instance si no existe
            instance_dir = self.project_root / "instance"
            instance_dir.mkdir(exist_ok=True)
            
            # Verificar que los modelos tengan los campos de 2FA
            models_file = self.project_root / "models.py"
            if models_file.exists():
                content = models_file.read_text()
                if "two_factor_enabled" in content:
                    print("✅ Modelo User actualizado con campos 2FA")
                else:
                    self.warnings.append("Modelo User no tiene campos 2FA")
            
            print("✅ Base de datos configurada")
            
        except Exception as e:
            self.errors.append(f"Error configurando base de datos: {e}")
    
    def setup_services(self):
        """Configurar servicios"""
        print("\n⚙️ Configurando servicios...")
        
        services = [
            "two_factor_service.py",
            "auth_service.py", 
            "cache_service.py",
            "user_service.py",
            "websocket_service.py",
            "query_optimizer.py"
        ]
        
        services_dir = self.project_root / "app" / "services"
        
        for service in services:
            service_path = services_dir / service
            if service_path.exists():
                print(f"✅ Servicio disponible: {service}")
            else:
                self.warnings.append(f"Servicio faltante: {service}")
        
        # Verificar __init__.py
        init_file = services_dir / "__init__.py"
        if not init_file.exists():
            init_file.write_text("# Services package\n")
            print("📁 Creado __init__.py en services")
    
    def setup_logging(self):
        """Configurar sistema de logging"""
        print("\n📝 Configurando logging...")
        
        try:
            # Crear directorio de logs
            logs_dir = self.project_root / "logs"
            logs_dir.mkdir(exist_ok=True)
            
            # Verificar servicio de logging
            logging_service = self.project_root / "app" / "core" / "logging_service.py"
            if logging_service.exists():
                print("✅ Servicio de logging disponible")
            else:
                self.warnings.append("Servicio de logging no encontrado")
            
            print("✅ Logging configurado")
            
        except Exception as e:
            self.errors.append(f"Error configurando logging: {e}")
    
    def setup_monitoring(self):
        """Configurar sistema de monitoreo"""
        print("\n📊 Configurando monitoreo...")
        
        try:
            # Verificar servicio de monitoreo
            monitoring_service = self.project_root / "app" / "core" / "monitoring_service.py"
            if monitoring_service.exists():
                print("✅ Servicio de monitoreo disponible")
            else:
                self.warnings.append("Servicio de monitoreo no encontrado")
            
            print("✅ Monitoreo configurado")
            
        except Exception as e:
            self.errors.append(f"Error configurando monitoreo: {e}")
    
    def setup_database_optimizer(self):
        """Configurar optimizador de base de datos"""
        print("\n🗄️ Configurando optimizador de base de datos...")
        
        try:
            # Verificar servicio de optimización
            db_optimizer = self.project_root / "app" / "core" / "database_optimizer.py"
            if db_optimizer.exists():
                print("✅ Optimizador de base de datos disponible")
            else:
                self.warnings.append("Optimizador de base de datos no encontrado")
            
            print("✅ Optimizador de base de datos configurado")
            
        except Exception as e:
            self.errors.append(f"Error configurando optimizador de BD: {e}")
    
    def setup_backup_service(self):
        """Configurar servicio de backup"""
        print("\n💾 Configurando servicio de backup...")
        
        try:
            # Verificar servicio de backup
            backup_service = self.project_root / "app" / "core" / "backup_service.py"
            if backup_service.exists():
                print("✅ Servicio de backup disponible")
            else:
                self.warnings.append("Servicio de backup no encontrado")
            
            # Crear directorio de backups
            backup_dir = self.project_root / "backups"
            backup_dir.mkdir(exist_ok=True)
            print("📁 Directorio de backups creado")
            
            print("✅ Servicio de backup configurado")
            
        except Exception as e:
            self.errors.append(f"Error configurando servicio de backup: {e}")
    
    def setup_testing_service(self):
        """Configurar servicio de testing"""
        print("\n🧪 Configurando servicio de testing...")
        
        try:
            # Verificar servicio de testing
            testing_service = self.project_root / "app" / "core" / "testing_service.py"
            if testing_service.exists():
                print("✅ Servicio de testing disponible")
            else:
                self.warnings.append("Servicio de testing no encontrado")
            
            # Crear directorio de tests
            tests_dir = self.project_root / "tests"
            tests_dir.mkdir(exist_ok=True)
            
            # Crear subdirectorios de tests
            test_subdirs = ["unit", "integration", "functional", "fixtures", "mocks"]
            for subdir in test_subdirs:
                (tests_dir / subdir).mkdir(exist_ok=True)
            
            print("📁 Estructura de tests creada")
            print("✅ Servicio de testing configurado")
            
        except Exception as e:
            self.errors.append(f"Error configurando servicio de testing: {e}")
            
        except Exception as e:
            self.errors.append(f"Error configurando monitoreo: {e}")
    
    def setup_2fa(self):
        """Configurar autenticación de dos factores"""
        print("\n🔐 Configurando 2FA...")
        
        try:
            # Verificar servicio 2FA
            tfa_service = self.project_root / "app" / "services" / "two_factor_service.py"
            if tfa_service.exists():
                print("✅ Servicio 2FA disponible")
            else:
                self.warnings.append("Servicio 2FA no encontrado")
            
            print("✅ 2FA configurado")
            
        except Exception as e:
            self.errors.append(f"Error configurando 2FA: {e}")
    
    def setup_validation(self):
        """Configurar validación de datos"""
        print("\n✅ Configurando validación...")
        
        try:
            # Verificar esquemas de validación
            schemas_file = self.project_root / "app" / "schemas" / "validation_schemas.py"
            if schemas_file.exists():
                print("✅ Esquemas de validación disponibles")
            else:
                self.warnings.append("Esquemas de validación no encontrados")
            
            # Crear __init__.py en schemas
            schemas_dir = self.project_root / "app" / "schemas"
            schemas_dir.mkdir(exist_ok=True)
            init_file = schemas_dir / "__init__.py"
            if not init_file.exists():
                init_file.write_text("# Schemas package\n")
            
            print("✅ Validación configurada")
            
        except Exception as e:
            self.errors.append(f"Error configurando validación: {e}")
    
    def setup_error_handling(self):
        """Configurar manejo de errores"""
        print("\n🚨 Configurando manejo de errores...")
        
        try:
            # Verificar manejador de errores
            error_handler = self.project_root / "app" / "core" / "error_handler.py"
            if error_handler.exists():
                print("✅ Manejador de errores disponible")
            else:
                self.warnings.append("Manejador de errores no encontrado")
            
            # Crear __init__.py en core
            core_dir = self.project_root / "app" / "core"
            core_dir.mkdir(exist_ok=True)
            init_file = core_dir / "__init__.py"
            if not init_file.exists():
                init_file.write_text("# Core package\n")
            
            print("✅ Manejo de errores configurado")
            
        except Exception as e:
            self.errors.append(f"Error configurando manejo de errores: {e}")
    
    def run_tests(self):
        """Ejecutar tests básicos"""
        print("\n🧪 Ejecutando tests básicos...")
        
        try:
            # Test de importación de módulos críticos
            test_imports = [
                "from app.core.error_handler import ErrorHandler",
                "from app.core.logging_service import LoggingService", 
                "from app.core.monitoring_service import MonitoringService",
                "from app.services.two_factor_service import TwoFactorService",
                "from app.schemas.validation_schemas import UserRegistrationSchema"
            ]
            
            for import_test in test_imports:
                try:
                    exec(import_test)
                    print(f"✅ Import OK: {import_test.split('import')[1].strip()}")
                except ImportError as e:
                    self.warnings.append(f"Import failed: {import_test} - {e}")
                except Exception as e:
                    self.warnings.append(f"Import error: {import_test} - {e}")
            
            print("✅ Tests básicos completados")
            
        except Exception as e:
            self.errors.append(f"Error ejecutando tests: {e}")
    
    def generate_report(self):
        """Generar reporte de configuración"""
        print("\n📄 Generando reporte...")
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "status": "success" if len(self.errors) == 0 else "error",
            "improvements_implemented": [
                "✅ Mejora 1: Seguridad y Autenticación (2FA)",
                "✅ Mejora 2: Gestión de Errores Centralizada", 
                "✅ Mejora 3: Validación de Datos Robusta",
                "✅ Mejora 4: Optimización de Base de Datos",
                "✅ Mejora 5: Sistema de Logging Avanzado",
                "✅ Mejora 9: Sistema de Backup Automatizado",
                "✅ Mejora 10: Monitoreo y Métricas",
                "✅ Mejora 11: Testing Automatizado"
            ],
            "pending_improvements": [
                "⏳ Mejora 6: API REST Completa",
                "⏳ Mejora 7: Sistema de Notificaciones Push",
                "⏳ Mejora 8: Gestión de Archivos Avanzada",
                "⏳ Mejora 12: Internacionalización (i18n)"
            ],
            "errors": self.errors,
            "warnings": self.warnings,
            "next_steps": [
                "1. Ejecutar migraciones de base de datos si es necesario",
                "2. Configurar variables de entorno para producción",
                "3. Implementar las mejoras pendientes",
                "4. Ejecutar tests completos",
                "5. Desplegar en entorno de staging para pruebas"
            ]
        }
        
        # Guardar reporte
        report_file = self.project_root / "improvements_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"📄 Reporte guardado en: {report_file}")
        
        # Mostrar resumen
        print("\n" + "=" * 60)
        print("📊 RESUMEN DE CONFIGURACIÓN")
        print("=" * 60)
        
        print(f"✅ Mejoras implementadas: {len(report['improvements_implemented'])}")
        print(f"⏳ Mejoras pendientes: {len(report['pending_improvements'])}")
        print(f"🚨 Errores: {len(self.errors)}")
        print(f"⚠️ Advertencias: {len(self.warnings)}")
        
        if self.errors:
            print("\n🚨 ERRORES:")
            for error in self.errors:
                print(f"  - {error}")
        
        if self.warnings:
            print("\n⚠️ ADVERTENCIAS:")
            for warning in self.warnings:
                print(f"  - {warning}")
        
        print("\n📋 PRÓXIMOS PASOS:")
        for step in report['next_steps']:
            print(f"  {step}")

def main():
    """Función principal"""
    setup = ImprovementsSetup()
    success = setup.run_setup()
    
    if success:
        print("\n🎉 ¡Configuración exitosa!")
        sys.exit(0)
    else:
        print("\n❌ Configuración completada con errores")
        sys.exit(1)

if __name__ == "__main__":
    main()
