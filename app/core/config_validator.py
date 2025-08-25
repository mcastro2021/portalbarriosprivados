"""
Validador de configuración
"""

import os
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class ConfigValidationResult:
    """Resultado de validación de configuración"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    missing_optional: List[str]


class ConfigValidator:
    """Validador de configuración de la aplicación"""
    
    # Configuraciones requeridas
    REQUIRED_CONFIG = {
        'SECRET_KEY': {
            'type': str,
            'min_length': 32,
            'description': 'Clave secreta para sesiones y JWT'
        },
        'SQLALCHEMY_DATABASE_URI': {
            'type': str,
            'pattern': r'^(sqlite|postgresql|mysql)://',
            'description': 'URI de conexión a la base de datos'
        }
    }
    
    # Configuraciones opcionales pero recomendadas
    OPTIONAL_CONFIG = {
        'MAIL_SERVER': {
            'type': str,
            'description': 'Servidor SMTP para envío de emails'
        },
        'MAIL_USERNAME': {
            'type': str,
            'description': 'Usuario SMTP'
        },
        'MAIL_PASSWORD': {
            'type': str,
            'description': 'Contraseña SMTP'
        },
        'MERCADOPAGO_ACCESS_TOKEN': {
            'type': str,
            'description': 'Token de acceso de MercadoPago'
        },
        'CLAUDE_API_KEY': {
            'type': str,
            'description': 'API Key de Claude para chatbot'
        },
        'TWILIO_ACCOUNT_SID': {
            'type': str,
            'description': 'SID de cuenta Twilio para WhatsApp'
        },
        'TWILIO_AUTH_TOKEN': {
            'type': str,
            'description': 'Token de autenticación Twilio'
        }
    }
    
    # Configuraciones de seguridad
    SECURITY_CONFIG = {
        'SESSION_COOKIE_SECURE': {
            'type': bool,
            'production_required': True,
            'description': 'Cookies seguras en producción'
        },
        'WTF_CSRF_ENABLED': {
            'type': bool,
            'default': True,
            'description': 'Protección CSRF habilitada'
        }
    }
    
    @classmethod
    def validate_config(cls, config: Dict[str, Any], environment: str = 'development') -> ConfigValidationResult:
        """
        Validar configuración completa
        
        Args:
            config: Diccionario de configuración
            environment: Entorno (development, production, testing)
        
        Returns:
            ConfigValidationResult con el resultado de la validación
        """
        errors = []
        warnings = []
        missing_optional = []
        
        # Validar configuraciones requeridas
        for key, requirements in cls.REQUIRED_CONFIG.items():
            error = cls._validate_config_item(config, key, requirements, required=True)
            if error:
                errors.append(error)
        
        # Validar configuraciones opcionales
        for key, requirements in cls.OPTIONAL_CONFIG.items():
            if key not in config or not config[key]:
                missing_optional.append(f"{key}: {requirements['description']}")
            else:
                error = cls._validate_config_item(config, key, requirements, required=False)
                if error:
                    warnings.append(error)
        
        # Validar configuraciones de seguridad
        for key, requirements in cls.SECURITY_CONFIG.items():
            if environment == 'production' and requirements.get('production_required'):
                error = cls._validate_config_item(config, key, requirements, required=True)
                if error:
                    errors.append(error)
            else:
                error = cls._validate_config_item(config, key, requirements, required=False)
                if error:
                    warnings.append(error)
        
        # Validaciones específicas por entorno
        if environment == 'production':
            prod_errors, prod_warnings = cls._validate_production_config(config)
            errors.extend(prod_errors)
            warnings.extend(prod_warnings)
        
        return ConfigValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            missing_optional=missing_optional
        )
    
    @classmethod
    def _validate_config_item(cls, config: Dict[str, Any], key: str, requirements: Dict[str, Any], required: bool = True) -> Optional[str]:
        """Validar un item de configuración específico"""
        
        # Verificar existencia
        if key not in config or config[key] is None:
            if required:
                return f"Configuración requerida faltante: {key} - {requirements['description']}"
            return None
        
        value = config[key]
        
        # Validar tipo
        expected_type = requirements.get('type')
        if expected_type and not isinstance(value, expected_type):
            return f"Tipo incorrecto para {key}: esperado {expected_type.__name__}, obtenido {type(value).__name__}"
        
        # Validar longitud mínima
        min_length = requirements.get('min_length')
        if min_length and isinstance(value, str) and len(value) < min_length:
            return f"Longitud insuficiente para {key}: mínimo {min_length} caracteres"
        
        # Validar patrón
        pattern = requirements.get('pattern')
        if pattern and isinstance(value, str) and not re.match(pattern, value):
            return f"Formato inválido para {key}: debe coincidir con {pattern}"
        
        return None
    
    @classmethod
    def _validate_production_config(cls, config: Dict[str, Any]) -> tuple[List[str], List[str]]:
        """Validaciones específicas para producción"""
        errors = []
        warnings = []
        
        # Verificar que SECRET_KEY no sea el valor por defecto
        secret_key = config.get('SECRET_KEY', '')
        if 'dev-secret-key' in secret_key or 'change-in-production' in secret_key:
            errors.append("SECRET_KEY debe cambiarse en producción")
        
        # Verificar base de datos de producción
        db_uri = config.get('SQLALCHEMY_DATABASE_URI', '')
        if 'sqlite' in db_uri.lower():
            warnings.append("SQLite no es recomendado para producción, considere PostgreSQL")
        
        # Verificar configuración de email
        if not config.get('MAIL_SERVER'):
            warnings.append("Servidor de email no configurado - las notificaciones por email no funcionarán")
        
        # Verificar HTTPS
        if not config.get('SESSION_COOKIE_SECURE'):
            errors.append("SESSION_COOKIE_SECURE debe ser True en producción")
        
        return errors, warnings
    
    @classmethod
    def validate_environment_variables(cls) -> ConfigValidationResult:
        """Validar variables de entorno directamente"""
        env_config = {}
        
        # Recopilar variables de entorno relevantes
        for key in list(cls.REQUIRED_CONFIG.keys()) + list(cls.OPTIONAL_CONFIG.keys()) + list(cls.SECURITY_CONFIG.keys()):
            env_value = os.environ.get(key)
            if env_value is not None:
                # Convertir strings de boolean
                if env_value.lower() in ('true', 'false'):
                    env_config[key] = env_value.lower() == 'true'
                else:
                    env_config[key] = env_value
        
        # Determinar entorno
        environment = os.environ.get('FLASK_ENV', 'development')
        
        return cls.validate_config(env_config, environment)
    
    @classmethod
    def get_config_template(cls) -> str:
        """Generar template de archivo .env"""
        template_lines = [
            "# Configuración de Portal Barrios Privados",
            "# Copie este archivo como .env y complete los valores",
            "",
            "# === CONFIGURACIÓN REQUERIDA ===",
        ]
        
        for key, requirements in cls.REQUIRED_CONFIG.items():
            template_lines.append(f"# {requirements['description']}")
            template_lines.append(f"{key}=")
            template_lines.append("")
        
        template_lines.extend([
            "# === CONFIGURACIÓN OPCIONAL ===",
        ])
        
        for key, requirements in cls.OPTIONAL_CONFIG.items():
            template_lines.append(f"# {requirements['description']}")
            template_lines.append(f"#{key}=")
            template_lines.append("")
        
        template_lines.extend([
            "# === CONFIGURACIÓN DE SEGURIDAD ===",
        ])
        
        for key, requirements in cls.SECURITY_CONFIG.items():
            template_lines.append(f"# {requirements['description']}")
            default_value = requirements.get('default', '')
            template_lines.append(f"#{key}={default_value}")
            template_lines.append("")
        
        return "\n".join(template_lines)
    
    @classmethod
    def print_validation_report(cls, result: ConfigValidationResult):
        """Imprimir reporte de validación"""
        print("=" * 50)
        print("REPORTE DE VALIDACIÓN DE CONFIGURACIÓN")
        print("=" * 50)
        
        if result.is_valid:
            print("✅ Configuración válida")
        else:
            print("❌ Configuración inválida")
        
        if result.errors:
            print("\n🚨 ERRORES (deben corregirse):")
            for error in result.errors:
                print(f"  - {error}")
        
        if result.warnings:
            print("\n⚠️  ADVERTENCIAS (recomendado corregir):")
            for warning in result.warnings:
                print(f"  - {warning}")
        
        if result.missing_optional:
            print("\n💡 CONFIGURACIONES OPCIONALES FALTANTES:")
            for missing in result.missing_optional:
                print(f"  - {missing}")
        
        print("=" * 50)
