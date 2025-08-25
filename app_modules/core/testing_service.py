"""
Sistema de Testing Automatizado
Proporciona framework completo de testing para el sistema
"""

import unittest
import pytest
import json
import os
import tempfile
import shutil
from datetime import datetime
from pathlib import Path
from flask import Flask
from flask_testing import TestCase
from unittest.mock import Mock, patch, MagicMock
import coverage
import subprocess
import sys
from typing import Dict, List, Optional, Any

class TestingService:
    """Servicio de testing automatizado"""
    
    def __init__(self, app=None):
        self.app = app
        self.test_results = []
        self.coverage_data = {}
        self.test_config = {}
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Inicializar servicio con la aplicación"""
        self.app = app
        
        # Configurar directorio de tests
        self.test_dir = Path(app.config.get('TEST_DIR', 'tests'))
        self.test_dir.mkdir(exist_ok=True)
        
        # Configurar coverage
        self.setup_coverage()
        
        # Crear estructura de tests
        self.create_test_structure()
        
        print("✅ Servicio de testing inicializado")
    
    def setup_coverage(self):
        """Configurar coverage para análisis de cobertura"""
        self.cov = coverage.Coverage(
            source=['app', '.'],
            omit=[
                'tests/*',
                'venv/*',
                '*/venv/*',
                'migrations/*',
                '*/migrations/*',
                'instance/*',
                'backups/*'
            ]
        )
    
    def create_test_structure(self):
        """Crear estructura básica de tests"""
        test_dirs = [
            'unit',
            'integration', 
            'functional',
            'fixtures',
            'mocks'
        ]
        
        for test_dir in test_dirs:
            dir_path = self.test_dir / test_dir
            dir_path.mkdir(exist_ok=True)
            
            # Crear __init__.py
            init_file = dir_path / '__init__.py'
            if not init_file.exists():
                init_file.write_text('# Test package\n')
        
        # Crear conftest.py para pytest
        conftest_file = self.test_dir / 'conftest.py'
        if not conftest_file.exists():
            self.create_conftest_file(conftest_file)
        
        print("✅ Estructura de tests creada")
    
    def create_conftest_file(self, conftest_path: Path):
        """Crear archivo conftest.py para pytest"""
        conftest_content = '''"""
Configuración global de pytest
"""

import pytest
import tempfile
import os
from flask import Flask
from app import create_app
from models import db

@pytest.fixture
def app():
    """Crear aplicación de test"""
    # Crear base de datos temporal
    db_fd, db_path = tempfile.mkstemp()
    
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test-secret-key'
    })
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()
    
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    """Cliente de test"""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Runner de comandos CLI"""
    return app.test_cli_runner()

@pytest.fixture
def auth_headers():
    """Headers de autenticación para tests"""
    return {
        'Authorization': 'Bearer test-token',
        'Content-Type': 'application/json'
    }

@pytest.fixture
def sample_user_data():
    """Datos de usuario de ejemplo"""
    return {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'TestPassword123!',
        'first_name': 'Test',
        'last_name': 'User',
        'role': 'resident'
    }

@pytest.fixture
def sample_visit_data():
    """Datos de visita de ejemplo"""
    return {
        'visitor_name': 'Juan Pérez',
        'visitor_dni': '12345678',
        'visitor_phone': '+5491123456789',
        'purpose': 'Visita social',
        'expected_date': '2024-12-25',
        'expected_time': '15:00'
    }
'''
        conftest_path.write_text(conftest_content)
    
    def run_all_tests(self) -> Dict:
        """Ejecutar todos los tests"""
        print("🧪 Iniciando ejecución de todos los tests...")
        
        # Iniciar coverage
        self.cov.start()
        
        try:
            # Ejecutar tests unitarios
            unit_results = self.run_unit_tests()
            
            # Ejecutar tests de integración
            integration_results = self.run_integration_tests()
            
            # Ejecutar tests funcionales
            functional_results = self.run_functional_tests()
            
            # Detener coverage y generar reporte
            self.cov.stop()
            coverage_report = self.generate_coverage_report()
            
            # Compilar resultados
            results = {
                'timestamp': datetime.now().isoformat(),
                'status': 'completed',
                'summary': {
                    'total_tests': 0,
                    'passed': 0,
                    'failed': 0,
                    'skipped': 0,
                    'errors': 0
                },
                'unit_tests': unit_results,
                'integration_tests': integration_results,
                'functional_tests': functional_results,
                'coverage': coverage_report,
                'duration': 0
            }
            
            # Calcular totales
            for test_type in ['unit_tests', 'integration_tests', 'functional_tests']:
                if test_type in results and results[test_type]:
                    results['summary']['total_tests'] += results[test_type].get('total', 0)
                    results['summary']['passed'] += results[test_type].get('passed', 0)
                    results['summary']['failed'] += results[test_type].get('failed', 0)
                    results['summary']['skipped'] += results[test_type].get('skipped', 0)
                    results['summary']['errors'] += results[test_type].get('errors', 0)
            
            # Determinar estado general
            if results['summary']['failed'] > 0 or results['summary']['errors'] > 0:
                results['status'] = 'failed'
            elif results['summary']['total_tests'] == 0:
                results['status'] = 'no_tests'
            else:
                results['status'] = 'passed'
            
            # Guardar resultados
            self.test_results.append(results)
            self.save_test_results(results)
            
            print(f"✅ Tests completados: {results['summary']['passed']}/{results['summary']['total_tests']} pasaron")
            
            return results
            
        except Exception as e:
            self.cov.stop()
            error_results = {
                'timestamp': datetime.now().isoformat(),
                'status': 'error',
                'error': str(e),
                'summary': {'total_tests': 0, 'passed': 0, 'failed': 0, 'skipped': 0, 'errors': 1}
            }
            
            print(f"❌ Error ejecutando tests: {str(e)}")
            return error_results
    
    def run_unit_tests(self) -> Dict:
        """Ejecutar tests unitarios"""
        print("🔬 Ejecutando tests unitarios...")
        
        try:
            # Buscar archivos de test unitarios
            unit_test_dir = self.test_dir / 'unit'
            test_files = list(unit_test_dir.glob('test_*.py'))
            
            if not test_files:
                print("ℹ️ No se encontraron tests unitarios")
                return {'status': 'no_tests', 'total': 0, 'passed': 0, 'failed': 0, 'skipped': 0}
            
            # Ejecutar pytest en directorio unit
            result = subprocess.run([
                sys.executable, '-m', 'pytest', 
                str(unit_test_dir),
                '-v',
                '--tb=short',
                '--json-report',
                '--json-report-file=test_results_unit.json'
            ], capture_output=True, text=True, cwd=str(self.test_dir.parent))
            
            # Parsear resultados
            return self.parse_pytest_results('test_results_unit.json', 'unit')
            
        except Exception as e:
            print(f"❌ Error en tests unitarios: {str(e)}")
            return {'status': 'error', 'error': str(e)}
    
    def run_integration_tests(self) -> Dict:
        """Ejecutar tests de integración"""
        print("🔗 Ejecutando tests de integración...")
        
        try:
            integration_test_dir = self.test_dir / 'integration'
            test_files = list(integration_test_dir.glob('test_*.py'))
            
            if not test_files:
                print("ℹ️ No se encontraron tests de integración")
                return {'status': 'no_tests', 'total': 0, 'passed': 0, 'failed': 0, 'skipped': 0}
            
            result = subprocess.run([
                sys.executable, '-m', 'pytest',
                str(integration_test_dir),
                '-v',
                '--tb=short',
                '--json-report',
                '--json-report-file=test_results_integration.json'
            ], capture_output=True, text=True, cwd=str(self.test_dir.parent))
            
            return self.parse_pytest_results('test_results_integration.json', 'integration')
            
        except Exception as e:
            print(f"❌ Error en tests de integración: {str(e)}")
            return {'status': 'error', 'error': str(e)}
    
    def run_functional_tests(self) -> Dict:
        """Ejecutar tests funcionales"""
        print("⚙️ Ejecutando tests funcionales...")
        
        try:
            functional_test_dir = self.test_dir / 'functional'
            test_files = list(functional_test_dir.glob('test_*.py'))
            
            if not test_files:
                print("ℹ️ No se encontraron tests funcionales")
                return {'status': 'no_tests', 'total': 0, 'passed': 0, 'failed': 0, 'skipped': 0}
            
            result = subprocess.run([
                sys.executable, '-m', 'pytest',
                str(functional_test_dir),
                '-v',
                '--tb=short',
                '--json-report',
                '--json-report-file=test_results_functional.json'
            ], capture_output=True, text=True, cwd=str(self.test_dir.parent))
            
            return self.parse_pytest_results('test_results_functional.json', 'functional')
            
        except Exception as e:
            print(f"❌ Error en tests funcionales: {str(e)}")
            return {'status': 'error', 'error': str(e)}
    
    def parse_pytest_results(self, results_file: str, test_type: str) -> Dict:
        """Parsear resultados de pytest"""
        try:
            results_path = self.test_dir.parent / results_file
            
            if not results_path.exists():
                return {'status': 'no_results', 'total': 0, 'passed': 0, 'failed': 0, 'skipped': 0}
            
            with open(results_path, 'r') as f:
                data = json.load(f)
            
            summary = data.get('summary', {})
            
            results = {
                'status': 'completed',
                'type': test_type,
                'total': summary.get('total', 0),
                'passed': summary.get('passed', 0),
                'failed': summary.get('failed', 0),
                'skipped': summary.get('skipped', 0),
                'errors': summary.get('error', 0),
                'duration': data.get('duration', 0),
                'tests': []
            }
            
            # Agregar detalles de tests individuales
            for test in data.get('tests', []):
                results['tests'].append({
                    'name': test.get('nodeid', ''),
                    'outcome': test.get('outcome', ''),
                    'duration': test.get('duration', 0),
                    'error': test.get('call', {}).get('longrepr', '') if test.get('outcome') == 'failed' else None
                })
            
            # Limpiar archivo temporal
            results_path.unlink()
            
            return results
            
        except Exception as e:
            print(f"⚠️ Error parseando resultados de {test_type}: {str(e)}")
            return {'status': 'parse_error', 'error': str(e)}
    
    def generate_coverage_report(self) -> Dict:
        """Generar reporte de cobertura"""
        try:
            # Generar reporte de coverage
            coverage_dir = self.test_dir / 'coverage'
            coverage_dir.mkdir(exist_ok=True)
            
            # Reporte en texto
            with open(coverage_dir / 'coverage.txt', 'w') as f:
                self.cov.report(file=f)
            
            # Reporte HTML
            self.cov.html_report(directory=str(coverage_dir / 'html'))
            
            # Obtener datos de cobertura
            coverage_data = self.cov.get_data()
            total_coverage = self.cov.report()
            
            report = {
                'total_coverage': total_coverage,
                'files': {},
                'html_report': str(coverage_dir / 'html' / 'index.html'),
                'text_report': str(coverage_dir / 'coverage.txt')
            }
            
            # Detalles por archivo
            for filename in coverage_data.measured_files():
                analysis = self.cov.analysis2(filename)
                report['files'][filename] = {
                    'statements': len(analysis[1]),
                    'missing': len(analysis[3]),
                    'coverage': (len(analysis[1]) - len(analysis[3])) / len(analysis[1]) * 100 if analysis[1] else 0
                }
            
            print(f"📊 Cobertura de código: {total_coverage:.1f}%")
            
            return report
            
        except Exception as e:
            print(f"⚠️ Error generando reporte de cobertura: {str(e)}")
            return {'error': str(e)}
    
    def save_test_results(self, results: Dict):
        """Guardar resultados de tests"""
        try:
            results_file = self.test_dir / 'test_results.json'
            
            # Cargar resultados existentes
            if results_file.exists():
                with open(results_file, 'r') as f:
                    all_results = json.load(f)
            else:
                all_results = {'test_runs': []}
            
            # Agregar nuevos resultados
            all_results['test_runs'].append(results)
            
            # Mantener solo los últimos 10 resultados
            all_results['test_runs'] = all_results['test_runs'][-10:]
            
            # Guardar
            with open(results_file, 'w') as f:
                json.dump(all_results, f, indent=2, default=str)
            
            print(f"💾 Resultados guardados en: {results_file}")
            
        except Exception as e:
            print(f"⚠️ Error guardando resultados: {str(e)}")
    
    def create_sample_tests(self):
        """Crear tests de ejemplo"""
        print("📝 Creando tests de ejemplo...")
        
        # Test unitario de ejemplo
        self.create_sample_unit_test()
        
        # Test de integración de ejemplo
        self.create_sample_integration_test()
        
        # Test funcional de ejemplo
        self.create_sample_functional_test()
        
        print("✅ Tests de ejemplo creados")
    
    def create_sample_unit_test(self):
        """Crear test unitario de ejemplo"""
        unit_test_content = '''"""
Tests unitarios de ejemplo
"""

import pytest
from unittest.mock import Mock, patch
from app_modules.services.two_factor_service import TwoFactorService
from app_modules.core.error_handler import ValidationError

class TestTwoFactorService:
    """Tests para el servicio de 2FA"""
    
    def test_generate_secret(self):
        """Test generación de secreto"""
        secret = TwoFactorService.generate_secret()
        
        assert secret is not None
        assert len(secret) == 32
        assert isinstance(secret, str)
    
    def test_generate_qr_code(self):
        """Test generación de código QR"""
        user = Mock()
        user.email = 'test@example.com'
        user.username = 'testuser'
        
        secret = 'TESTSECRET123456789012345678901'
        
        result = TwoFactorService.generate_qr_code(user, secret)
        
        assert result['success'] is True
        assert 'qr_code' in result
        assert 'manual_entry_key' in result
    
    def test_validate_token_valid(self):
        """Test validación de token válido"""
        secret = 'TESTSECRET123456789012345678901'
        
        # Mock del token válido
        with patch('pyotp.TOTP.verify') as mock_verify:
            mock_verify.return_value = True
            
            result = TwoFactorService.validate_token(secret, '123456')
            
            assert result is True
            mock_verify.assert_called_once_with('123456', valid_window=1)
    
    def test_validate_token_invalid(self):
        """Test validación de token inválido"""
        secret = 'TESTSECRET123456789012345678901'
        
        with patch('pyotp.TOTP.verify') as mock_verify:
            mock_verify.return_value = False
            
            result = TwoFactorService.validate_token(secret, '000000')
            
            assert result is False

class TestValidationSchemas:
    """Tests para esquemas de validación"""
    
    def test_user_registration_valid_data(self):
        """Test validación de datos válidos de registro"""
        from app_modules.schemas.validation_schemas import UserRegistrationSchema
        
        schema = UserRegistrationSchema()
        valid_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'TestPassword123!',
            'first_name': 'Test',
            'last_name': 'User'
        }
        
        result = schema.load(valid_data)
        
        assert result['username'] == 'testuser'
        assert result['email'] == 'test@example.com'
    
    def test_user_registration_invalid_email(self):
        """Test validación con email inválido"""
        from app_modules.schemas.validation_schemas import UserRegistrationSchema
        from marshmallow import ValidationError
        
        schema = UserRegistrationSchema()
        invalid_data = {
            'username': 'testuser',
            'email': 'invalid-email',
            'password': 'TestPassword123!',
            'first_name': 'Test',
            'last_name': 'User'
        }
        
        with pytest.raises(ValidationError) as exc_info:
            schema.load(invalid_data)
        
        assert 'email' in exc_info.value.messages
'''
        
        unit_test_file = self.test_dir / 'unit' / 'test_services.py'
        unit_test_file.write_text(unit_test_content)
    
    def create_sample_integration_test(self):
        """Crear test de integración de ejemplo"""
        integration_test_content = '''"""
Tests de integración de ejemplo
"""

import pytest
import json
from models import db, User

class TestUserAPI:
    """Tests de integración para API de usuarios"""
    
    def test_user_registration_flow(self, client, app):
        """Test flujo completo de registro de usuario"""
        with app.app_context():
            # Datos de registro
            user_data = {
                'username': 'newuser',
                'email': 'newuser@example.com',
                'password': 'NewPassword123!',
                'first_name': 'New',
                'last_name': 'User'
            }
            
            # Realizar registro
            response = client.post('/api/v1/auth/register', 
                                 data=json.dumps(user_data),
                                 content_type='application/json')
            
            assert response.status_code == 201
            
            # Verificar que el usuario fue creado
            user = User.query.filter_by(email='newuser@example.com').first()
            assert user is not None
            assert user.username == 'newuser'
    
    def test_user_login_flow(self, client, app):
        """Test flujo completo de login"""
        with app.app_context():
            # Crear usuario de prueba
            user = User(
                username='testuser',
                email='test@example.com',
                first_name='Test',
                last_name='User'
            )
            user.set_password('TestPassword123!')
            db.session.add(user)
            db.session.commit()
            
            # Intentar login
            login_data = {
                'email': 'test@example.com',
                'password': 'TestPassword123!'
            }
            
            response = client.post('/api/v1/auth/login',
                                 data=json.dumps(login_data),
                                 content_type='application/json')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'access_token' in data

class TestDatabaseIntegration:
    """Tests de integración con base de datos"""
    
    def test_user_crud_operations(self, app):
        """Test operaciones CRUD de usuario"""
        with app.app_context():
            # Create
            user = User(
                username='cruduser',
                email='crud@example.com',
                first_name='CRUD',
                last_name='User'
            )
            user.set_password('CrudPassword123!')
            db.session.add(user)
            db.session.commit()
            
            user_id = user.id
            
            # Read
            retrieved_user = User.query.get(user_id)
            assert retrieved_user is not None
            assert retrieved_user.username == 'cruduser'
            
            # Update
            retrieved_user.first_name = 'Updated'
            db.session.commit()
            
            updated_user = User.query.get(user_id)
            assert updated_user.first_name == 'Updated'
            
            # Delete
            db.session.delete(updated_user)
            db.session.commit()
            
            deleted_user = User.query.get(user_id)
            assert deleted_user is None
'''
        
        integration_test_file = self.test_dir / 'integration' / 'test_api.py'
        integration_test_file.write_text(integration_test_content)
    
    def create_sample_functional_test(self):
        """Crear test funcional de ejemplo"""
        functional_test_content = '''"""
Tests funcionales de ejemplo
"""

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

class TestWebInterface:
    """Tests funcionales de la interfaz web"""
    
    @pytest.fixture
    def driver(self):
        """Configurar driver de Selenium"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        driver = webdriver.Chrome(options=chrome_options)
        yield driver
        driver.quit()
    
    def test_home_page_loads(self, driver, app):
        """Test que la página principal carga correctamente"""
        with app.test_client() as client:
            # Iniciar servidor de desarrollo para tests
            driver.get("http://localhost:5000")
            
            # Verificar que el título es correcto
            assert "Portal Barrios Privados" in driver.title
            
            # Verificar elementos principales
            assert driver.find_element(By.TAG_NAME, "body")
    
    def test_login_form_validation(self, driver, app):
        """Test validación del formulario de login"""
        with app.test_client() as client:
            driver.get("http://localhost:5000/login")
            
            # Intentar enviar formulario vacío
            login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            login_button.click()
            
            # Verificar mensajes de validación
            wait = WebDriverWait(driver, 10)
            error_message = wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "error-message"))
            )
            
            assert error_message.is_displayed()

class TestUserWorkflow:
    """Tests de flujos de usuario completos"""
    
    def test_complete_user_registration_workflow(self, client, app):
        """Test flujo completo de registro y activación"""
        with app.app_context():
            # Paso 1: Registro inicial
            registration_data = {
                'username': 'workflowuser',
                'email': 'workflow@example.com',
                'password': 'WorkflowPassword123!',
                'first_name': 'Workflow',
                'last_name': 'User'
            }
            
            response = client.post('/register', data=registration_data)
            assert response.status_code in [200, 302]  # Success or redirect
            
            # Paso 2: Verificar usuario creado pero inactivo
            from models import User
            user = User.query.filter_by(email='workflow@example.com').first()
            assert user is not None
            assert not user.is_active  # Usuario debe estar inactivo inicialmente
            
            # Paso 3: Simular activación
            user.is_active = True
            from models import db
            db.session.commit()
            
            # Paso 4: Login con usuario activado
            login_data = {
                'email': 'workflow@example.com',
                'password': 'WorkflowPassword123!'
            }
            
            response = client.post('/login', data=login_data)
            assert response.status_code in [200, 302]
'''
        
        functional_test_file = self.test_dir / 'functional' / 'test_workflows.py'
        functional_test_file.write_text(functional_test_content)
    
    def get_test_status(self) -> Dict:
        """Obtener estado actual de los tests"""
        try:
            results_file = self.test_dir / 'test_results.json'
            
            if not results_file.exists():
                return {
                    'status': 'no_tests_run',
                    'message': 'No se han ejecutado tests aún'
                }
            
            with open(results_file, 'r') as f:
                data = json.load(f)
            
            if not data.get('test_runs'):
                return {
                    'status': 'no_tests_run',
                    'message': 'No hay resultados de tests'
                }
            
            # Obtener último resultado
            latest_run = data['test_runs'][-1]
            
            return {
                'status': latest_run.get('status', 'unknown'),
                'last_run': latest_run.get('timestamp'),
                'summary': latest_run.get('summary', {}),
                'coverage': latest_run.get('coverage', {}).get('total_coverage', 0),
                'total_runs': len(data['test_runs'])
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def run_specific_test(self, test_path: str) -> Dict:
        """Ejecutar un test específico"""
        try:
            print(f"🧪 Ejecutando test específico: {test_path}")
            
            result = subprocess.run([
                sys.executable, '-m', 'pytest',
                test_path,
                '-v',
                '--tb=short'
            ], capture_output=True, text=True, cwd=str(self.test_dir.parent))
            
            return {
                'status': 'completed',
                'exit_code': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'success': result.returncode == 0
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }

# Instancia global del servicio
testing_service = TestingService()
