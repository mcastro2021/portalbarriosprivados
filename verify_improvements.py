#!/usr/bin/env python3
"""
Script de verificación de mejoras críticas implementadas
"""

import os
import sys
import importlib
from datetime import datetime


def print_header(title):
    """Imprimir header decorado"""
    print("\n" + "=" * 60)
    print(f"🔍 {title}")
    print("=" * 60)


def print_result(test_name, success, details=""):
    """Imprimir resultado de test"""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} {test_name}")
    if details:
        print(f"    {details}")


def test_imports():
    """Verificar que todos los módulos se pueden importar"""
    print_header("VERIFICACIÓN DE IMPORTS")
    
    modules_to_test = [
        ('app.services.auth_service', 'AuthService'),
        ('app.services.security_service', 'SecurityService'),
        ('app.core.error_handler', 'ErrorHandler'),
        ('app.core.config_validator', 'ConfigValidator'),
    ]
    
    all_passed = True
    
    for module_name, class_name in modules_to_test:
        try:
            module = importlib.import_module(module_name)
            cls = getattr(module, class_name)
            print_result(f"Import {module_name}.{class_name}", True)
        except Exception as e:
            print_result(f"Import {module_name}.{class_name}", False, str(e))
            all_passed = False
    
    return all_passed


def test_auth_service():
    """Verificar funcionalidades del AuthService"""
    print_header("VERIFICACIÓN DE AUTH SERVICE")
    
    try:
        from app.services.auth_service import AuthService
        
        # Test validación de contraseña
        valid_password = "TestPassword123!"
        is_valid, message = AuthService.validate_password(valid_password)
        print_result("Validación de contraseña válida", is_valid)
        
        # Test validación de email
        valid_email = "test@example.com"
        email_valid = AuthService.validate_email(valid_email)
        print_result("Validación de email válido", email_valid)
        
        # Test hash de contraseña
        hashed = AuthService.hash_password(valid_password)
        hash_check = AuthService.check_password(hashed, valid_password)
        print_result("Hash y verificación de contraseña", hash_check)
        
        # Test sanitización
        dangerous_input = "<script>alert('xss')</script>"
        sanitized = AuthService.sanitize_input(dangerous_input)
        sanitization_ok = "script" not in sanitized
        print_result("Sanitización de input", sanitization_ok)
        
        # Test generación de token seguro
        token = AuthService.generate_secure_token()
        token_ok = len(token) > 20
        print_result("Generación de token seguro", token_ok)
        
        return True
        
    except Exception as e:
        print_result("AuthService tests", False, str(e))
        return False


def test_security_service():
    """Verificar funcionalidades del SecurityService"""
    print_header("VERIFICACIÓN DE SECURITY SERVICE")
    
    try:
        from app.services.security_service import SecurityService
        
        # Test validación de IP
        valid_ip = "192.168.1.1"
        ip_valid = SecurityService.validate_ip_address(valid_ip)
        print_result("Validación de IP válida", ip_valid)
        
        invalid_ip = "999.999.999.999"
        ip_invalid = not SecurityService.validate_ip_address(invalid_ip)
        print_result("Validación de IP inválida", ip_invalid)
        
        # Test URL segura
        safe_url = "/dashboard"
        url_safe = SecurityService.is_safe_redirect_url(safe_url)
        print_result("Validación de URL segura", url_safe)
        
        dangerous_url = "javascript:alert('xss')"
        url_dangerous = not SecurityService.is_safe_redirect_url(dangerous_url)
        print_result("Detección de URL peligrosa", url_dangerous)
        
        # Test estadísticas de seguridad
        stats = SecurityService.get_security_stats()
        stats_ok = isinstance(stats, dict) and 'active_ips' in stats
        print_result("Generación de estadísticas", stats_ok)
        
        return True
        
    except Exception as e:
        print_result("SecurityService tests", False, str(e))
        return False


def test_config_validator():
    """Verificar funcionalidades del ConfigValidator"""
    print_header("VERIFICACIÓN DE CONFIG VALIDATOR")
    
    try:
        from app.core.config_validator import ConfigValidator
        
        # Test configuración básica
        test_config = {
            'SECRET_KEY': 'a' * 32,  # 32 caracteres mínimo
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///test.db'
        }
        
        result = ConfigValidator.validate_config(test_config)
        validation_ok = hasattr(result, 'is_valid')
        print_result("Validación de configuración", validation_ok)
        
        # Test generación de template
        template = ConfigValidator.get_config_template()
        template_ok = len(template) > 100 and 'SECRET_KEY' in template
        print_result("Generación de template", template_ok)
        
        return True
        
    except Exception as e:
        print_result("ConfigValidator tests", False, str(e))
        return False


def test_error_handler():
    """Verificar funcionalidades del ErrorHandler"""
    print_header("VERIFICACIÓN DE ERROR HANDLER")
    
    try:
        from app.core.error_handler import ErrorHandler, ValidationError, BusinessLogicError, SecurityError
        
        # Test excepciones personalizadas
        try:
            raise ValidationError("Test error", field="test_field")
        except ValidationError as e:
            validation_error_ok = e.field == "test_field"
            print_result("ValidationError personalizada", validation_error_ok)
        
        try:
            raise BusinessLogicError("Test business error")
        except BusinessLogicError as e:
            business_error_ok = "business error" in str(e)
            print_result("BusinessLogicError personalizada", business_error_ok)
        
        try:
            raise SecurityError("Test security error")
        except SecurityError as e:
            security_error_ok = "security error" in str(e)
            print_result("SecurityError personalizada", security_error_ok)
        
        return True
        
    except Exception as e:
        print_result("ErrorHandler tests", False, str(e))
        return False


def test_file_structure():
    """Verificar estructura de archivos"""
    print_header("VERIFICACIÓN DE ESTRUCTURA DE ARCHIVOS")
    
    required_files = [
        'app/services/__init__.py',
        'app/services/auth_service.py',
        'app/services/security_service.py',
        'app/core/__init__.py',
        'app/core/error_handler.py',
        'app/core/config_validator.py',
        'tests/__init__.py',
        'tests/test_auth_service.py',
        'pytest.ini',
        'setup_config.py',
        'README_MEJORAS_CRITICAS.md'
    ]
    
    all_files_exist = True
    
    for file_path in required_files:
        exists = os.path.exists(file_path)
        print_result(f"Archivo {file_path}", exists)
        if not exists:
            all_files_exist = False
    
    return all_files_exist


def test_dependencies():
    """Verificar dependencias críticas"""
    print_header("VERIFICACIÓN DE DEPENDENCIAS")
    
    critical_deps = [
        'jwt',
        'pytest',
        'alembic',
        'marshmallow'
    ]
    
    all_deps_ok = True
    
    for dep in critical_deps:
        try:
            importlib.import_module(dep)
            print_result(f"Dependencia {dep}", True)
        except ImportError:
            print_result(f"Dependencia {dep}", False, "No instalada")
            all_deps_ok = False
    
    return all_deps_ok


def run_all_tests():
    """Ejecutar todas las verificaciones"""
    print("🏠 Portal Barrios Privados - Verificación de Mejoras Críticas")
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        ("Estructura de archivos", test_file_structure),
        ("Dependencias críticas", test_dependencies),
        ("Imports de módulos", test_imports),
        ("AuthService", test_auth_service),
        ("SecurityService", test_security_service),
        ("ConfigValidator", test_config_validator),
        ("ErrorHandler", test_error_handler),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print_result(f"ERROR en {test_name}", False, str(e))
            results.append((test_name, False))
    
    # Resumen final
    print_header("RESUMEN DE VERIFICACIÓN")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n📊 Resultado: {passed}/{total} tests pasaron")
    
    if passed == total:
        print("🎉 ¡Todas las mejoras críticas están funcionando correctamente!")
        print("\n📋 Próximos pasos:")
        print("1. Ejecutar: python setup_config.py (si no lo ha hecho)")
        print("2. Ejecutar: pytest (para tests completos)")
        print("3. Ejecutar: python app.py (para iniciar la aplicación)")
        return True
    else:
        print("⚠️  Algunas verificaciones fallaron. Revise los errores arriba.")
        print("\n🔧 Soluciones sugeridas:")
        print("1. Instalar dependencias: pip install -r requirements.txt")
        print("2. Verificar estructura: ls -la app/ tests/")
        print("3. Revisar imports: python -c 'from app.services import *'")
        return False


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
