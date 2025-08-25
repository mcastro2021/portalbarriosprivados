"""
Tests para AuthService
"""

import pytest
from unittest.mock import patch, MagicMock
from app_modules.services.auth_service import AuthService


class TestAuthService:
    """Tests para el servicio de autenticación"""
    
    def test_validate_password_valid(self):
        """Test validación de contraseña válida"""
        password = "MiPassword123!"
        is_valid, message = AuthService.validate_password(password)
        assert is_valid is True
        assert message == "Contraseña válida"
    
    def test_validate_password_too_short(self):
        """Test contraseña muy corta"""
        password = "123"
        is_valid, message = AuthService.validate_password(password)
        assert is_valid is False
        assert "al menos 8 caracteres" in message
    
    def test_validate_password_no_uppercase(self):
        """Test contraseña sin mayúsculas"""
        password = "mipassword123!"
        is_valid, message = AuthService.validate_password(password)
        assert is_valid is False
        assert "mayúscula" in message
    
    def test_validate_password_no_lowercase(self):
        """Test contraseña sin minúsculas"""
        password = "MIPASSWORD123!"
        is_valid, message = AuthService.validate_password(password)
        assert is_valid is False
        assert "minúscula" in message
    
    def test_validate_password_no_number(self):
        """Test contraseña sin números"""
        password = "MiPassword!"
        is_valid, message = AuthService.validate_password(password)
        assert is_valid is False
        assert "número" in message
    
    def test_validate_password_no_special_char(self):
        """Test contraseña sin caracteres especiales"""
        password = "MiPassword123"
        is_valid, message = AuthService.validate_password(password)
        assert is_valid is False
        assert "carácter especial" in message
    
    def test_validate_email_valid(self):
        """Test validación de email válido"""
        email = "usuario@ejemplo.com"
        assert AuthService.validate_email(email) is True
    
    def test_validate_email_invalid(self):
        """Test validación de email inválido"""
        invalid_emails = [
            "usuario@",
            "@ejemplo.com",
            "usuario.ejemplo.com",
            "usuario@ejemplo",
            ""
        ]
        
        for email in invalid_emails:
            assert AuthService.validate_email(email) is False
    
    def test_sanitize_input_basic(self):
        """Test sanitización básica de entrada"""
        dangerous_input = "<script>alert('xss')</script>"
        sanitized = AuthService.sanitize_input(dangerous_input)
        assert "script" not in sanitized
        assert "alert" not in sanitized
    
    def test_sanitize_input_empty(self):
        """Test sanitización de entrada vacía"""
        assert AuthService.sanitize_input("") == ""
        assert AuthService.sanitize_input(None) == ""
    
    def test_hash_password(self):
        """Test hash de contraseña"""
        password = "MiPassword123!"
        hashed = AuthService.hash_password(password)
        
        assert hashed != password
        assert len(hashed) > 50  # Hash debe ser largo
        assert AuthService.check_password(hashed, password) is True
    
    def test_check_password_invalid(self):
        """Test verificación de contraseña incorrecta"""
        password = "MiPassword123!"
        wrong_password = "OtraPassword456!"
        hashed = AuthService.hash_password(password)
        
        assert AuthService.check_password(hashed, wrong_password) is False
    
    def test_generate_secure_token(self):
        """Test generación de token seguro"""
        token1 = AuthService.generate_secure_token()
        token2 = AuthService.generate_secure_token()
        
        assert len(token1) > 20
        assert len(token2) > 20
        assert token1 != token2  # Deben ser únicos
    
    @patch('app.services.auth_service.current_app')
    def test_generate_jwt_token(self, mock_app):
        """Test generación de token JWT"""
        mock_app.config = {'SECRET_KEY': 'test-secret-key'}
        mock_app.logger = MagicMock()
        
        token = AuthService.generate_jwt_token(user_id=1, role='user')
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 50
    
    @patch('app.services.auth_service.current_app')
    def test_verify_jwt_token_valid(self, mock_app):
        """Test verificación de token JWT válido"""
        mock_app.config = {'SECRET_KEY': 'test-secret-key'}
        mock_app.logger = MagicMock()
        
        # Generar token
        token = AuthService.generate_jwt_token(user_id=1, role='user')
        
        # Verificar token
        payload = AuthService.verify_jwt_token(token)
        
        assert 'error' not in payload
        assert payload['user_id'] == 1
        assert payload['role'] == 'user'
    
    @patch('app.services.auth_service.current_app')
    def test_verify_jwt_token_invalid(self, mock_app):
        """Test verificación de token JWT inválido"""
        mock_app.config = {'SECRET_KEY': 'test-secret-key'}
        mock_app.logger = MagicMock()
        
        invalid_token = "token.invalido.aqui"
        payload = AuthService.verify_jwt_token(invalid_token)
        
        assert 'error' in payload
        assert payload['error'] == 'Token inválido'


@pytest.fixture
def mock_request():
    """Mock del objeto request de Flask"""
    with patch('app.services.auth_service.request') as mock_req:
        mock_req.headers = {}
        mock_req.args = {}
        yield mock_req


class TestAuthDecorators:
    """Tests para decoradores de autenticación"""
    
    @patch('app.services.auth_service.request')
    @patch('app.services.auth_service.jsonify')
    def test_jwt_required_no_token(self, mock_jsonify, mock_request):
        """Test decorador JWT sin token"""
        mock_request.headers = {}
        mock_request.args = {}
        mock_jsonify.return_value = MagicMock()
        
        @AuthService.jwt_required
        def test_function():
            return "success"
        
        result = test_function()
        
        # Verificar que se llamó jsonify con error
        mock_jsonify.assert_called_once()
        call_args = mock_jsonify.call_args[0][0]
        assert 'error' in call_args
        assert 'Token requerido' in call_args['error']
    
    @patch('app.services.auth_service.request')
    @patch('app.services.auth_service.jsonify')
    @patch('app.services.auth_service.AuthService.verify_jwt_token')
    def test_jwt_required_invalid_token(self, mock_verify, mock_jsonify, mock_request):
        """Test decorador JWT con token inválido"""
        mock_request.headers = {'Authorization': 'Bearer invalid_token'}
        mock_request.args = {}
        mock_verify.return_value = {'error': 'Token inválido'}
        mock_jsonify.return_value = MagicMock()
        
        @AuthService.jwt_required
        def test_function():
            return "success"
        
        result = test_function()
        
        mock_jsonify.assert_called_once()
        call_args = mock_jsonify.call_args[0][0]
        assert 'error' in call_args
    
    @patch('app.services.auth_service.request')
    @patch('app.services.auth_service.AuthService.verify_jwt_token')
    def test_jwt_required_valid_token(self, mock_verify, mock_request):
        """Test decorador JWT con token válido"""
        mock_request.headers = {'Authorization': 'Bearer valid_token'}
        mock_request.args = {}
        mock_verify.return_value = {'user_id': 1, 'role': 'user'}
        
        @AuthService.jwt_required
        def test_function():
            return "success"
        
        result = test_function()
        
        assert result == "success"
        assert hasattr(mock_request, 'jwt_user_id')
        assert mock_request.jwt_user_id == 1
        assert mock_request.jwt_role == 'user'
