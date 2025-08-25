"""
Servicio de autenticación de dos factores (2FA)
Implementa TOTP (Time-based One-Time Password) para mayor seguridad
"""

import pyotp
import qrcode
import io
import base64
from datetime import datetime, timedelta
from flask import current_app
from models import db, User
import secrets
import string

class TwoFactorService:
    """Servicio para gestionar autenticación de dos factores"""
    
    @staticmethod
    def generate_secret():
        """Generar secreto para TOTP"""
        return pyotp.random_base32()
    
    @staticmethod
    def generate_qr_code(user, secret):
        """Generar código QR para configurar 2FA"""
        try:
            # Crear URI para TOTP
            totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
                name=user.email,
                issuer_name=current_app.config.get('BARRIO_NAME', 'Portal Barrio Privado')
            )
            
            # Generar código QR
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(totp_uri)
            qr.make(fit=True)
            
            # Convertir a imagen
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convertir a base64
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            qr_code_data = base64.b64encode(buffer.getvalue()).decode()
            
            return {
                'success': True,
                'qr_code': qr_code_data,
                'secret': secret,
                'uri': totp_uri
            }
            
        except Exception as e:
            current_app.logger.error(f'Error generando QR code: {str(e)}')
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def verify_token(secret, token):
        """Verificar token TOTP"""
        try:
            totp = pyotp.TOTP(secret)
            # Verificar token actual y tokens de ventana de tiempo (±1 período)
            return totp.verify(token, valid_window=1)
        except Exception as e:
            current_app.logger.error(f'Error verificando token 2FA: {str(e)}')
            return False
    
    @staticmethod
    def enable_2fa(user, secret, verification_token):
        """Habilitar 2FA para un usuario"""
        try:
            # Verificar token antes de habilitar
            if not TwoFactorService.verify_token(secret, verification_token):
                return {
                    'success': False,
                    'error': 'Token de verificación inválido'
                }
            
            # Guardar secreto en el usuario
            user.two_factor_secret = secret
            user.two_factor_enabled = True
            user.two_factor_enabled_at = datetime.utcnow()
            user.updated_at = datetime.utcnow()
            
            # Generar códigos de respaldo
            backup_codes = TwoFactorService.generate_backup_codes()
            user.two_factor_backup_codes = ','.join(backup_codes)
            
            db.session.commit()
            
            return {
                'success': True,
                'message': '2FA habilitado exitosamente',
                'backup_codes': backup_codes
            }
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error habilitando 2FA: {str(e)}')
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def disable_2fa(user, verification_token=None, backup_code=None):
        """Deshabilitar 2FA para un usuario"""
        try:
            # Verificar token o código de respaldo
            if verification_token:
                if not TwoFactorService.verify_token(user.two_factor_secret, verification_token):
                    return {
                        'success': False,
                        'error': 'Token de verificación inválido'
                    }
            elif backup_code:
                if not TwoFactorService.verify_backup_code(user, backup_code):
                    return {
                        'success': False,
                        'error': 'Código de respaldo inválido'
                    }
            else:
                return {
                    'success': False,
                    'error': 'Se requiere token de verificación o código de respaldo'
                }
            
            # Deshabilitar 2FA
            user.two_factor_secret = None
            user.two_factor_enabled = False
            user.two_factor_enabled_at = None
            user.two_factor_backup_codes = None
            user.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            return {
                'success': True,
                'message': '2FA deshabilitado exitosamente'
            }
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Error deshabilitando 2FA: {str(e)}')
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def generate_backup_codes(count=10):
        """Generar códigos de respaldo"""
        codes = []
        for _ in range(count):
            # Generar código de 8 caracteres
            code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
            codes.append(code)
        return codes
    
    @staticmethod
    def verify_backup_code(user, code):
        """Verificar código de respaldo"""
        try:
            if not user.two_factor_backup_codes:
                return False
            
            backup_codes = user.two_factor_backup_codes.split(',')
            
            if code.upper() in [c.upper() for c in backup_codes]:
                # Remover código usado
                backup_codes = [c for c in backup_codes if c.upper() != code.upper()]
                user.two_factor_backup_codes = ','.join(backup_codes)
                user.updated_at = datetime.utcnow()
                db.session.commit()
                return True
            
            return False
            
        except Exception as e:
            current_app.logger.error(f'Error verificando código de respaldo: {str(e)}')
            return False
    
    @staticmethod
    def is_required_for_user(user):
        """Verificar si 2FA es requerido para el usuario"""
        # 2FA obligatorio para administradores
        if user.role == 'admin':
            return True
        
        # 2FA opcional para otros usuarios
        return False
    
    @staticmethod
    def get_user_2fa_status(user):
        """Obtener estado de 2FA del usuario"""
        return {
            'enabled': getattr(user, 'two_factor_enabled', False),
            'required': TwoFactorService.is_required_for_user(user),
            'enabled_at': getattr(user, 'two_factor_enabled_at', None),
            'backup_codes_count': len(getattr(user, 'two_factor_backup_codes', '').split(',')) if getattr(user, 'two_factor_backup_codes', '') else 0
        }
    
    @staticmethod
    def validate_login_with_2fa(user, token=None, backup_code=None):
        """Validar login con 2FA"""
        try:
            # Si 2FA no está habilitado, permitir login
            if not getattr(user, 'two_factor_enabled', False):
                return {
                    'success': True,
                    'requires_2fa': False
                }
            
            # Si no se proporciona token ni código de respaldo, requerir 2FA
            if not token and not backup_code:
                return {
                    'success': False,
                    'requires_2fa': True,
                    'message': 'Se requiere código de autenticación de dos factores'
                }
            
            # Verificar token TOTP
            if token:
                if TwoFactorService.verify_token(user.two_factor_secret, token):
                    return {
                        'success': True,
                        'requires_2fa': False,
                        'method': 'totp'
                    }
            
            # Verificar código de respaldo
            if backup_code:
                if TwoFactorService.verify_backup_code(user, backup_code):
                    return {
                        'success': True,
                        'requires_2fa': False,
                        'method': 'backup_code'
                    }
            
            return {
                'success': False,
                'requires_2fa': True,
                'message': 'Código de autenticación inválido'
            }
            
        except Exception as e:
            current_app.logger.error(f'Error validando login con 2FA: {str(e)}')
            return {
                'success': False,
                'requires_2fa': True,
                'message': 'Error en la validación de 2FA'
            }
